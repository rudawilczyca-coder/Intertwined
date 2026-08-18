#!/usr/bin/env python3
"""Embed the tracked Intertwined card metadata into its PNG artwork.

The source JSON is human-readable and reviewable. The generated PNG contains
both SillyTavern's ``chara`` (v2 compatibility) and ``ccv3`` text chunks while
preserving every non-card chunk from the source image.
"""
import argparse
import base64
import copy
import json
import os
import struct
import tempfile
import zlib


PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
CARD_KEYWORDS = {b"chara", b"ccv3"}


def read_chunks(path):
    with open(path, "rb") as handle:
        if handle.read(8) != PNG_SIGNATURE:
            raise ValueError("source image is not a PNG")
        while True:
            raw_length = handle.read(4)
            if not raw_length:
                raise ValueError("PNG ended before IEND")
            length = struct.unpack(">I", raw_length)[0]
            kind = handle.read(4)
            data = handle.read(length)
            crc = handle.read(4)
            if len(kind) != 4 or len(data) != length or len(crc) != 4:
                raise ValueError("truncated PNG chunk")
            yield kind, data
            if kind == b"IEND":
                break


def png_chunk(kind, data):
    checksum = zlib.crc32(kind)
    checksum = zlib.crc32(data, checksum) & 0xFFFFFFFF
    return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", checksum)


def with_legacy_mirrors(card):
    """Match SillyTavern exports by including v2-era top-level mirrors."""
    result = copy.deepcopy(card)
    data = result["data"]
    for field in ("name", "description", "personality", "scenario", "first_mes",
                  "mes_example", "tags"):
        result[field] = copy.deepcopy(data.get(field, ""))
    result["creatorcomment"] = data.get("creator_notes", "")
    result["avatar"] = "none"
    result["chat"] = ""
    result["talkativeness"] = data.get("extensions", {}).get("talkativeness", "0.5")
    result["fav"] = bool(data.get("extensions", {}).get("fav", False))
    return result


def encoded_card(card):
    raw = json.dumps(card, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    return base64.b64encode(raw)


def build(source_json, source_png, output_png):
    with open(source_json, encoding="utf-8") as handle:
        v3 = json.load(handle)
    if v3.get("spec") != "chara_card_v3" or not isinstance(v3.get("data"), dict):
        raise ValueError("source JSON must be a chara_card_v3 object")

    v3 = with_legacy_mirrors(v3)
    v2 = copy.deepcopy(v3)
    v2["spec"] = "chara_card_v2"
    v2["spec_version"] = "2.0"
    metadata = {
        b"chara": encoded_card(v2),
        b"ccv3": encoded_card(v3),
    }

    output_dir = os.path.dirname(os.path.abspath(output_png))
    os.makedirs(output_dir, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=".intertwined-card-", suffix=".png", dir=output_dir)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(PNG_SIGNATURE)
            for kind, data in read_chunks(source_png):
                if kind == b"tEXt" and data.split(b"\0", 1)[0] in CARD_KEYWORDS:
                    continue
                if kind == b"IEND":
                    for keyword in (b"chara", b"ccv3"):
                        handle.write(png_chunk(b"tEXt", keyword + b"\0" + metadata[keyword]))
                handle.write(png_chunk(kind, data))
        os.replace(temporary, output_png)
    except Exception:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", default=os.path.join(here, "intertwined_character_card.json"))
    parser.add_argument("--image", required=True, help="existing card PNG whose artwork is preserved")
    parser.add_argument("--output", required=True, help="generated card PNG; may equal --image")
    args = parser.parse_args()
    build(os.path.abspath(args.source), os.path.abspath(args.image), os.path.abspath(args.output))
    print("built %s" % os.path.abspath(args.output))


if __name__ == "__main__":
    main()
