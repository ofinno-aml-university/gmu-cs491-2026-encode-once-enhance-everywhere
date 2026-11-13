import cv2  # Version 5.0.0
import numpy  # Version 2.5.4
import onnxruntime  # Version 1.31.1


def upscale_y4m_frames(
    y_frames: numpy.ndarray,
    u_frames: numpy.ndarray,
    v_frames: numpy.ndarray,
    session: onnxruntime.InferenceSession,
    scale_factor: int = 2,
):
    """
    Upscale YUV (Y4M) frames using FSRCNNX ONNX model.

    Args:
        y_frames: NumPy array of shape (N, H, W), dtype uint8.
        u_frames: NumPy array of shape (N, H_uv, W_uv), dtype uint8.
        v_frames: NumPy array of shape (N, H_uv, W_uv), dtype uint8.
        session: Initialized onnxruntime inference session object
        scale_factor: Upscaling factor of the specific FSRCNNX model (typically 2, 3, or 4).

    Returns:
        Tuple of upscaled (y_out, u_out, v_out) uint8 NumPy arrays.

    Raises:
        TypeError: If arrays passed in are not NumPy
        ValueError: If NumPy arrays are invalid due to any of the following:
            * Frame arrays don't have shape (N, H, W)
            * Frame arrays don't have matching number of frames
            * U and V frame arrays don't have matching dimensions
    """

    # Argument error handling

    if not isinstance(y_frames, numpy.ndarray):
        raise TypeError("y_frames must be a NumPy array")

    if not isinstance(u_frames, numpy.ndarray):
        raise TypeError("u_frames must be a NumPy array")

    if not isinstance(v_frames, numpy.ndarray):
        raise TypeError("v_frames must be a NumPy array")

    if y_frames.ndim != 3:
        raise ValueError("y_frames must have shape (N, H, W)")

    if u_frames.ndim != 3 or v_frames.ndim != 3:
        raise ValueError("U and V frames must have shape (N, H, W)")

    if y_frames.shape[0] != u_frames.shape[0] or y_frames.shape[0] != v_frames.shape[0]:
        raise ValueError("Y, U, and V must contain the same number of frames")

    if u_frames.shape != v_frames.shape:
        raise ValueError("U and V arrays must have matching dimensions")

    input_name = session.get_inputs()[0].name

    num_frames, h, w = y_frames.shape
    _, h_uv, w_uv = u_frames.shape

    out_h, out_w = h * scale_factor, w * scale_factor
    out_h_uv, out_w_uv = h_uv * scale_factor, w_uv * scale_factor

    # Pre-allocate output arrays
    y_out = numpy.empty((num_frames, out_h, out_w), dtype=numpy.uint8)
    u_out = numpy.empty((num_frames, out_h_uv, out_w_uv), dtype=numpy.uint8)
    v_out = numpy.empty((num_frames, out_h_uv, out_w_uv), dtype=numpy.uint8)

    for i in range(num_frames):
        # Preprocess Y channel: normalize [0, 255] -> [0.0, 1.0] and add batch/channel dims (1, 1, H, W)
        y_in = y_frames[i].astype(numpy.float32) / 255.0
        y_in = y_in[numpy.newaxis, numpy.newaxis, :, :]

        # Run ONNX inference on the Y channel
        y_pred = session.run(None, {input_name: y_in})[0]

        # Postprocess Y channel: remove batch/channel dims, clip, and convert back to uint8
        y_pred = numpy.squeeze(y_pred)
        y_out[i] = numpy.clip(y_pred * 255.0, 0, 255).astype(numpy.uint8)

        # Upscale U and V chroma channels using bicubic interpolation
        u_out[i] = cv2.resize(
            u_frames[i], (out_w_uv, out_h_uv), interpolation=cv2.INTER_CUBIC
        )
        v_out[i] = cv2.resize(
            v_frames[i], (out_w_uv, out_h_uv), interpolation=cv2.INTER_CUBIC
        )

    return y_out, u_out, v_out
