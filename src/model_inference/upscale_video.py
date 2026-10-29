import cv2  # currently version 5.0.0 using numpy 2.5.4
import argparse


def parse_command_line_arguments():
    parser = argparse.ArgumentParser(description="Apply ESPCN to a given video file")

    parser.add_argument(
        "-i",
        "--input",
        required=True,
        type=str,
        help="The video file to be upscaled",
    )
    parser.add_argument(
        "-m",
        "--model",
        type=str,
        default="ESPCN_x2.pb",
        help=".pb file for the model to use for upscaling",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default="output-video-2x.mp4",
        help="Desired name of the upscaled video file",
    )

    return parser.parse_args()


def upscale_video(input_video_path, output_video_path, model_path, scale=2):
    # Initialize the OpenCV DNN Super Resolution object
    sr = cv2.dnn_superres.DnnSuperResImpl_create()

    # Load the ESPCN model weights
    print(f"[INFO] Loading ESPCN model from: {model_path}")
    sr.readModel(model_path)
    sr.setModel("espcn", scale)

    # Open the source low-resolution video
    cap = cv2.VideoCapture(input_video_path)
    if not cap.isOpened():
        print("[ERROR] Could not open input video.")
        return

    # Extract original video properties
    fps = cap.get(cv2.CAP_PROP_FPS)
    orig_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    orig_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Calculate target upscale dimensions
    target_width = orig_width * scale
    target_height = orig_height * scale

    # Set up the Video Writer for the upscaled output
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")  # Codec for .mp4
    out = cv2.VideoWriter(output_video_path, fourcc, fps, (target_width, target_height))

    print(
        f"[INFO] Upscaling: {orig_width}x{orig_height} -> {target_width}x{target_height} at {fps} FPS"
    )

    frame_count = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break  # End of video file

        # Pass the frame through the ESPCN neural network
        upscaled_frame = sr.upsample(frame)

        # Save the upscaled frame to the output file
        out.write(upscaled_frame)

        frame_count += 1
        if frame_count % 30 == 0:
            print(f"[INFO] Processed {frame_count} frames...")

    # Clean up resources
    cap.release()
    out.release()
    cv2.destroyAllWindows()
    print("[SUCCESS] Video upscaling completed successfully.")


if __name__ == "__main__":
    parsed_args = parse_command_line_arguments()

    upscale_video(parsed_args.input, parsed_args.output, parsed_args.model, 2)
