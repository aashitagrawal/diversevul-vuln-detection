"""
Step 4 (Improvement B): rename identifiers to generic names.

Idea: the paper guesses that models fail on unseen projects because they
memorize project-specific names (e.g. "gnutls_session_t", "yyg->yy_c_buf_p").
If we replace those names with generic ones, the model can't rely on them and
must learn from the code structure instead.

    session->security_parameters  ->  VAR_1->VAR_2
    _gnutls_hash_get_algo_len(x)   ->  FUNC_1(VAR_3)

What we KEEP unchanged:
  - C/C++ keywords (if, for, int, struct, ...)
  - common standard library names (memcpy, strcpy, malloc, free, NULL, ...),
    because these are often exactly where memory bugs happen
  - string and character literals
Comments are removed.

The same name always gets the same placeholder inside one function.

Try it:
    python src/rename_ids.py
"""

import re

KEEP = set("""
auto break case char const continue default do double else enum extern float for goto if
inline int long register restrict return short signed sizeof static struct switch typedef
union unsigned void volatile while bool true false class namespace template typename this
new delete public private protected virtual operator try catch throw nullptr using
const_cast static_cast dynamic_cast reinterpret_cast
NULL size_t ssize_t uint8_t uint16_t uint32_t uint64_t int8_t int16_t int32_t int64_t
uintptr_t FILE errno std string vector
malloc calloc realloc free alloca memcpy memmove memset memcmp memchr
strcpy strncpy strcat strncat strcmp strncmp strlen strnlen strchr strrchr strstr strdup
sprintf snprintf vsprintf vsnprintf printf fprintf scanf sscanf gets fgets puts
read write open close fopen fclose fread fwrite
assert abort exit atoi atol strtol strtoul
kmalloc kzalloc kfree vmalloc vfree copy_from_user copy_to_user
""".split())

# One regex that finds, in order: comments, string literals, char literals, identifiers
TOKEN = re.compile(r"""
    (?P<comment>/\*.*?\*/|//[^\n]*)
  | (?P<string>"(?:\\.|[^"\\])*")
  | (?P<char>'(?:\\.|[^'\\])*')
  | (?P<ident>[A-Za-z_]\w*)
""", re.DOTALL | re.VERBOSE)

CALL = re.compile(r"\s*\(")  # optional spaces, then "("


def rename_identifiers(code):
    names = {}  # original name -> placeholder, for this one function
    counts = {"FUNC": 0, "VAR": 0}

    def replace(m):
        if m.group("comment"):
            return ""
        if m.group("string") or m.group("char"):
            return m.group(0)
        name = m.group("ident")
        if name in KEEP:
            return name
        if name not in names:
            # It's a function name if the next non-space character is "("
            kind = "FUNC" if CALL.match(code, m.end()) else "VAR"
            counts[kind] += 1
            names[name] = f"{kind}_{counts[kind]}"
        return names[name]

    return TOKEN.sub(replace, code)


if __name__ == "__main__":
    example = '''static int png_read_chunk(png_structp png_ptr, char *buf, size_t len)
{
    /* copy the chunk */
    char tmp[MAX_CHUNK];
    if (len > MAX_CHUNK)
        return png_error(png_ptr, "chunk too big");
    memcpy(tmp, buf, len);
    return 0;
}'''
    print("BEFORE:\n" + example)
    print("\nAFTER:\n" + rename_identifiers(example))
