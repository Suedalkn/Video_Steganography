"""CLI entrypoint for embedding, extraction and evaluation."""

from __future__ import annotations

import argparse
from pathlib import Path

from src.config import load_config
from src.embedder import embed_message
from src.evaluator import (
    compute_psnr_for_videos,
    compute_ssim_for_videos,
    extraction_accuracy,
    write_report,
)
from src.extractor import extract_message
from src.logger import append_development_log, setup_logger
from src.video_loader import load_video_frames, write_video_frames


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Adaptive DWT-DCT video steganography")
    parser.add_argument("--config", type=Path, default=Path("config.yaml"))
    parser.add_argument("--mode", choices=["embed", "extract", "evaluate"], required=True)
    parser.add_argument("--message", type=str, default="")
    parser.add_argument("--video", type=Path, default=None)
    parser.add_argument("--stego", type=Path, default=None)
    parser.add_argument("--truth", type=str, default="")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    config = load_config(args.config)
    logger = setup_logger(config.paths.process_log, config.raw["project"]["log_level"])

    input_video = args.video or config.paths.input_video
    stego_video = args.stego or config.paths.stego_video

    if args.mode == "embed":
        if not args.message:
            raise ValueError("--message is required in embed mode.")
        frames, fps = load_video_frames(input_video, config.raw["video"]["max_frames"])
        stego_frames = embed_message(frames, args.message, config, logger)
        write_video_frames(
            stego_video,
            stego_frames,
            fps,
            preferred_codec=config.raw["video"].get("output_codec", "FFV1"),
        )
        write_video_frames(
            config.paths.stego_preview_video,
            stego_frames,
            fps,
            preferred_codec="mp4v",
        )
        append_development_log(
            config.paths.development_log,
            "TEST: Embed run completed | Result: Lossless stego + preview stego generated.",
        )
        print(f"Stego video written to: {stego_video}")

    elif args.mode == "extract":
        frames, _ = load_video_frames(stego_video, config.raw["video"]["max_frames"])
        reference_frames = None
        if input_video.exists():
            reference_frames, _ = load_video_frames(input_video, config.raw["video"]["max_frames"])
        message = extract_message(frames, config, logger, reference_frames=reference_frames)
        config.paths.extracted_text.write_text(message, encoding="utf-8")
        append_development_log(
            config.paths.development_log,
            "TEST: Extract run completed | Result: Message extracted and saved.",
        )
        print(message)

    elif args.mode == "evaluate":
        original_frames, _ = load_video_frames(input_video, config.raw["video"]["max_frames"])
        stego_frames, _ = load_video_frames(stego_video, config.raw["video"]["max_frames"])
        extracted = (
            config.paths.extracted_text.read_text(encoding="utf-8")
            if config.paths.extracted_text.exists()
            else extract_message(stego_frames, config, logger, reference_frames=original_frames)
        )
        psnr_value = compute_psnr_for_videos(original_frames, stego_frames)
        report = {
            "psnr": psnr_value,
            "accuracy": extraction_accuracy(args.truth, extracted) if args.truth else -1,
        }
        if config.raw["evaluation"]["compute_ssim"]:
            report["ssim"] = compute_ssim_for_videos(original_frames, stego_frames)
        write_report(config.paths.report_json, report)
        append_development_log(
            config.paths.development_log,
            "TEST: Evaluation run completed | Result: Metrics report generated.",
        )
        print(report)


if __name__ == "__main__":
    main()
