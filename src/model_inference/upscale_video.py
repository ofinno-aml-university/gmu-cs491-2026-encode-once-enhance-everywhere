import cv2  # currently version 5.0.0 using numpy 2.5.4
import argparse
import os


def parse_command_line_arguments():
    """Parse command-line arguments.

    Define the required and optional arguments for the upscaling model.

    Args:
        none.

    Returns:
        An argparse.Namespace object that holds the command-line arguments as attributes.
    """

    # initialize argparse object
    parser = argparse.ArgumentParser(description="Apply ESPCN to a given video file")

    # add required video input argument
    parser.add_argument(
        "-i",
        "--input",
        required=True,
        type=str,
        help="The video file to be upscaled",
    )

    # add optional model selection argument (won't be used until later)
    parser.add_argument(
        "-m",
        "--model",
        type=str,
        default="FSRCNN_x2.pb",
        help=".pb file for the model to use for upscaling",
    )

    # add output file name argument
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default="output-video-2x.mp4",
        help="Desired name of the upscaled video file",
    )

    # return parsed args
    return parser.parse_args()


def load_model(model_path: str, scale: int):
    """Initialize the super resolution object.

    Args:
        model_path: Path to the .pb model file.
        scale: Integer upscaling factor.

    Returns:
        The initialized super resolution object with the model loaded.

    Raises:
        FileNotFoundError: If the .pb file was not found in the given path.
        ValueError: If the model file is the wrong format.
    """

    # check if the given path exists
    if not os.path.exists(model_path):
        raise FileNotFoundError(
            f"Model file not found at {os.path.abspath(model_path)}"
        )

    # check if model file is in correct format
    if not model_path.endswith(".pb"):
        raise ValueError("Model file must be in Protocol Buffer (.pb) format")

    # initialize super resolution object
    sr = cv2.dnn_superres.DnnSuperResImpl_create()

    # try to read the given model
    try:
        sr.readModel(model_path)
        sr.setModel("fsrcnn", scale)

        return sr

    # if OpenCV encounters an error, print it and return none
    except cv2.error as e:
        print("[OpenCV Error] Failed to parse or initialize model")
        print(f"Details: {e}")

        return None


def load_video_file(input_video_path: str):
    """Initialize video capture object and connects a video file to it.

    Args:
        input_video_path: Path to the video file.

    Returns:
        The initialized VideoCapture object with the loaded video file.

    Raises:
        FileNotFoundError: If the video file was not found in the given path.
        ValueError: If the given file is not a video file.
    """

    # check if the given path exists
    if not os.path.exists(input_video_path):
        raise FileNotFoundError(
            f"Video file not found at {os.path.abspath(input_video_path)}"
        )

    # check that given file is in a video format
    video_extensions = {".mp4", ".mkv", ".avi", ".mov", ".flv", ".wmv", ".webm", ".m4v"}
    _, ext = os.path.splitext(input_video_path)
    if ext not in video_extensions:
        raise ValueError(
            "Input file does not have a video extension (.mp4, .mov, .webm, etc.)"
        )

    # initialize video capture object with the given video file
    # return none on error
    cap = cv2.VideoCapture(input_video_path)
    if not cap.isOpened():
        print("[ERROR] Could not open input video.")
        return None

    return cap


def upscale_video(
    input_video_path: str, output_video_path: str, model_path: str, scale: int
):
    """Upscale the video after reading the model and the input video

    Args:
    Returns:
    Raises:"""

    # get the super resolution object
    sr = load_model(model_path, scale)

    # check if model loaded successfully
    if sr == None:
        return

    # get video capture object
    cap = load_video_file(input_video_path)

    # check if video loaded successfully
    if cap == None:
        return

    # extract video properties
    fps = cap.get(cv2.CAP_PROP_FPS)
    original_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    original_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # calculate target dimensions
    target_width = original_width * scale
    target_height = original_height * scale

    # set up the Video Writer for the upscaled output
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")  # Codec for .mp4
    out = cv2.VideoWriter(output_video_path, fourcc, fps, (target_width, target_height))

    while True:
        # get the next frame
        ret, frame = cap.read()
        if not ret:
            break  # End of video file

        # pass the frame through the FSRCNN neural network
        upscaled_frame = sr.upsample(frame)

        # Save the upscaled frame to the output file
        out.write(upscaled_frame)

    # Clean up resources
    cap.release()
    out.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    parsed_args = parse_command_line_arguments()

    upscale_video(parsed_args.input, parsed_args.output, parsed_args.model, 2)
