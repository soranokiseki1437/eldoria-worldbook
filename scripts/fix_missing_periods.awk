BEGIN { in_context = 0; in_term = 0 }
/^情境:/ { in_context = 1; in_term = 0; print; next }
/^章节终止条件:/ { in_context = 0; in_term = 1; print; next }
/^[a-zA-Z]/ && !/^情境:/ && !/^章节终止条件:/ && !/^[0-9]\./ { in_context = 0; in_term = 0 }
{
    if ((in_context || in_term) && /^[[:space:]]/ && length > 2) {
        last = substr($0, length($0), 1)
        if (last !~ /[。！？…》"\x27)」\x2d]/) {
            print $0 "。"
        } else { print }
    } else { print }
}
