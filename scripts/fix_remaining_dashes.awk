# Fix ALL remaining em dashes in one pass
# Replaces —— with ， everywhere EXCEPT the 名称 field (title)
{
    # Skip 名称 field (keep dashes in titles)
    if (/^名称:/) { print; next }

    # Replace ALL —— in all other lines
    gsub(/——/, "，")
    print
}
