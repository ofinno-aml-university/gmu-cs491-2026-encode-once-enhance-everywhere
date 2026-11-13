"""Convert an FSRCNNX mpv shader (igv/FSRCNN-TensorFlow, release 1.1) to ONNX.

The released FSRCNNX weights ship inside GLSL shaders for the mpv player, not as
a TensorFlow graph. This script reads the weights out of the shader and rebuilds
the same network as a plain ONNX graph (Pad, Conv, PRelu, Add, DepthToSpace).

Model I/O
  input  "luma": float32 [N, 1, H, W], the Y plane scaled to 0..1 (8-bit Y / 255)
  output "luma_x2": float32 [N, 1, 2H, 2W], clipped to 0..1
The model upscales luma only. Upscale chroma separately (for example bicubic).

License note: the shader weights are LGPL-3.0 (see the shader header), so the
converted .onnx file is a derived work under the same license. Do not commit it
to an MIT-licensed repository; download and convert it at setup time instead.

Usage
  pip install onnx onnxruntime numpy pillow
  python fsrcnnx_to_onnx.py --variant 8-0-4-1 --out fsrcnnx_x2_8-0-4-1.onnx
  python fsrcnnx_to_onnx.py --variant 8-0-4-1 --out m.onnx --check-dir Test/Set5
"""
import argparse
import re
import urllib.request
from pathlib import Path

import numpy as np
import onnx
from onnx import TensorProto, helper, numpy_helper

RELEASE_URL = "https://github.com/igv/FSRCNN-TensorFlow/releases/download/1.1/FSRCNNX_x2_{}.glsl"

NUM = r"-?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?"
RE_BIAS = re.compile(r"vec4 res = vec4\(([^)]*)\);")
RE_MAT = re.compile(r"res \+= mat4(?:x4)?\(([^)]*)\) \* (\w+?)_texOff\((?:vec2\((-?\d+),\s*(-?\d+)\)|0)\);")
RE_VEC = re.compile(r"res \+= vec4\(([^)]*)\) \* float\((\w+?)_texOff\(vec2\((-?\d+),\s*(-?\d+)\)\)\);")
RE_RESID = re.compile(r"res \+= (\w+?)_texOff\(0\);")
RE_PRELU = re.compile(r"res = max\(res, vec4\(0\.0\)\) \+ vec4\(([^)]*)\) \* min\(res, vec4\(0\.0\)\);")


def floats(text):
    return [float(x) for x in re.findall(NUM, text)]


def parse_shader(text):
    """Split the shader into passes and collect weights, bias, residual and PReLU."""
    passes = []
    for block in text.split("//!HOOK")[1:]:
        hdr = dict(desc=None, binds=[], save=None)
        for line in block.splitlines():
            if line.startswith("//!DESC"):
                hdr["desc"] = line[7:].strip()
            elif line.startswith("//!BIND"):
                hdr["binds"].append(line[7:].strip())
            elif line.startswith("//!SAVE"):
                hdr["save"] = line[7:].strip()
        p = dict(hdr, terms=[], bias=None, resid=None, prelu=None)
        if hdr["desc"] == "aggregation":
            if "res[index.x * 2 + index.y]" not in block:
                raise ValueError("Unexpected aggregation pass; the shader format may have changed.")
            passes.append(p)
            continue
        p["bias"] = floats(RE_BIAS.search(block).group(1))
        for m in RE_MAT.finditer(block):
            dx, dy = (int(m.group(3)), int(m.group(4))) if m.group(3) else (0, 0)
            p["terms"].append(("mat", floats(m.group(1)), m.group(2), dx, dy))
        for m in RE_VEC.finditer(block):
            p["terms"].append(("vec", floats(m.group(1)), m.group(2), int(m.group(3)), int(m.group(4))))
        if m := RE_RESID.search(block):
            p["resid"] = m.group(1)
        if m := RE_PRELU.search(block):
            p["prelu"] = floats(m.group(1))
        passes.append(p)
    return passes


def build_onnx(passes, opset=13):
    """Turn the parsed passes into an ONNX graph. One shader pass = one 4-channel conv."""
    nodes, inits = [], []
    tensors = {"LUMA": "luma"}

    def const(name, arr):
        inits.append(numpy_helper.from_array(np.asarray(arr), name))
        return name

    for i, p in enumerate(passes):
        if p["desc"] == "aggregation":
            src = tensors[p["binds"][0]]
            # Shader: out(2X+ix, 2Y+iy) = SUBCONV[ix*2+iy]. DepthToSpace (CRD) wants channel iy*2+ix.
            nodes.append(helper.make_node("Gather", [src, const("perm", np.array([0, 2, 1, 3], np.int64))], ["d2s_in"], axis=1))
            nodes.append(helper.make_node("DepthToSpace", ["d2s_in"], ["x2_raw"], blocksize=2, mode="CRD"))
            nodes.append(helper.make_node("Clip", ["x2_raw", const("lo", np.float32(0)), const("hi", np.float32(1))], ["luma_x2"]))
            continue

        conv_in = [b for b in p["binds"] if any(t[2] == b for t in p["terms"])]
        chans = {b: (1 if b == "LUMA" else 4) for b in conv_in}
        offset, cin = {}, 0
        for b in conv_in:
            offset[b], cin = cin, cin + chans[b]
        r = max(max(abs(t[3]), abs(t[4])) for t in p["terms"])
        k = 2 * r + 1
        w = np.zeros((4, cin, k, k), np.float32)
        for kind, a, tex, dx, dy in p["terms"]:
            if kind == "vec":  # vec4(w) * float(LUMA): one input channel, four outputs
                w[:, offset[tex], dy + r, dx + r] += a
            else:  # GLSL mat4 is column-major: out[o] += a[4*j + o] * in[j]
                w[:, offset[tex]:offset[tex] + 4, dy + r, dx + r] += np.array(a, np.float32).reshape(4, 4).T

        x = tensors[conv_in[0]]
        if len(conv_in) > 1:
            x = f"cat{i}"
            nodes.append(helper.make_node("Concat", [tensors[b] for b in conv_in], [x], axis=1))
        if r > 0:  # mpv samples with clamp-to-edge, which is edge padding
            pads = const(f"pads{i}", np.array([0, 0, r, r, 0, 0, r, r], np.int64))
            nodes.append(helper.make_node("Pad", [x, pads], [f"pad{i}"], mode="edge"))
            x = f"pad{i}"
        out = f"conv{i}"
        nodes.append(helper.make_node("Conv", [x, const(f"w{i}", w), const(f"b{i}", np.array(p["bias"], np.float32))], [out]))
        if p["resid"]:
            nodes.append(helper.make_node("Add", [out, tensors[p["resid"]]], [f"res{i}"]))
            out = f"res{i}"
        if p["prelu"]:
            slope = const(f"alpha{i}", np.array(p["prelu"], np.float32).reshape(4, 1, 1))
            nodes.append(helper.make_node("PRelu", [out, slope], [f"act{i}"]))
            out = f"act{i}"
        tensors[p["save"]] = out

    graph = helper.make_graph(
        nodes, "fsrcnnx_x2",
        [helper.make_tensor_value_info("luma", TensorProto.FLOAT, ["N", 1, "H", "W"])],
        [helper.make_tensor_value_info("luma_x2", TensorProto.FLOAT, ["N", 1, "H2", "W2"])],
        inits)
    # IR version 8 keeps the file loadable by older ONNX Runtime releases too
    model = helper.make_model(graph, opset_imports=[helper.make_opsetid("", opset)],
                              producer_name="fsrcnnx_to_onnx", ir_version=8)
    onnx.checker.check_model(model)
    return model


def psnr(a, b):
    mse = np.mean((a.astype(np.float64) - b.astype(np.float64)) ** 2)
    return 10 * np.log10(255.0 ** 2 / mse)


def check(model_path, image_dir):
    """Sanity check: downscale 2x with bicubic, upscale with the model, compare to bicubic."""
    import onnxruntime as ort
    from PIL import Image
    sess = ort.InferenceSession(model_path, providers=["CPUExecutionProvider"])
    print(f"{'image':<24}{'bicubic':>10}{'FSRCNNX':>10}{'gain':>8}  (Y-PSNR dB, 2x)")
    gains = []
    for path in sorted(Path(image_dir).glob("*")):
        if path.suffix.lower() not in (".bmp", ".png", ".jpg"):
            continue
        y = Image.open(path).convert("L")
        w, h = y.width // 2 * 2, y.height // 2 * 2
        gt = np.asarray(y.crop((0, 0, w, h)))
        lr = Image.fromarray(gt).resize((w // 2, h // 2), Image.BICUBIC)
        bic = np.asarray(lr.resize((w, h), Image.BICUBIC))
        inp = (np.asarray(lr, np.float32) / 255.0)[None, None]
        sr = np.clip(np.round(sess.run(None, {"luma": inp})[0][0, 0] * 255.0), 0, 255)
        s = np.s_[4:-4, 4:-4]  # ignore a thin border, as usual for SR benchmarks
        pb, ps = psnr(gt[s], bic[s]), psnr(gt[s], sr[s])
        gains.append(ps - pb)
        print(f"{path.name:<24}{pb:>10.2f}{ps:>10.2f}{ps - pb:>+8.2f}")
    print(f"mean gain over bicubic: {np.mean(gains):+.2f} dB")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--variant", default="8-0-4-1", help="8-0-4-1 (faster) or 16-0-4-1 (stronger)")
    ap.add_argument("--shader", help="local .glsl file instead of downloading the release")
    ap.add_argument("--out", required=True, help="output .onnx path")
    ap.add_argument("--opset", type=int, default=13)
    ap.add_argument("--check-dir", help="folder of ground-truth images for a 2x PSNR sanity check")
    args = ap.parse_args()

    if args.shader:
        text = Path(args.shader).read_text()
    else:
        url = RELEASE_URL.format(args.variant)
        print(f"downloading {url}")
        text = urllib.request.urlopen(url).read().decode()
    passes = parse_shader(text)
    model = build_onnx(passes, args.opset)
    onnx.save(model, args.out)
    n_params = sum(np.prod(t.dims) for t in model.graph.initializer)
    print(f"saved {args.out}: {len(passes)} passes, {n_params} parameters")
    if args.check_dir:
        check(args.out, args.check_dir)


if __name__ == "__main__":
    main()
