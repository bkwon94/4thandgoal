"""
Write a copy of a PNG with one byte changed: the FLG byte of the zlib header of the first IDAT chunk.
The new FLG keeps a valid FCHECK, so the image still decodes; only the hash of the file changes.
"""
import struct, sys
src, dst = sys.argv[1], sys.argv[2]
b = bytearray(open(src, "rb").read())
i = 8
while True:
    n, = struct.unpack(">I", b[i:i + 4])
    if b[i + 4:i + 8] == b"IDAT":
        break
    i += 12 + n
pos = i + 9  # The FLG byte: 4 length bytes, 4 type bytes, then CMF, then FLG.
cmf, flg = b[pos - 1], b[pos]
level = (flg >> 6) & 3
for new_level in range(4):
    if new_level == level:
        continue
    base = (new_level << 6) | (flg & 0x20)
    new = base + (31 - ((cmf * 256 + base) % 31)) % 31
    if new != flg:
        break
print(f"offset {pos}: byte 0x{flg:02x} -> 0x{new:02x}")
b[pos] = new
open(dst, "wb").write(b)
