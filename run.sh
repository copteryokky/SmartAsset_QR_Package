#!/usr/bin/env bash
pip install pandas openpyxl "qrcode[pil]" reportlab Pillow
python build_pages_and_qr.py
