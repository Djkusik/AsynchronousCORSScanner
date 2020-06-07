import linecache

def normalize_url(i):
    if '://' in i:
        return [i]
    else:
        return ["http://" + i, "https://" + i]

def read_file(input_file):
    lines = linecache.getlines(input_file)
    return lines


def read_urls(path):
    urls = []
    lines = read_file(path)
    for i in lines:
        for u in normalize_url(i.strip()):
            urls.append(u)

    return urls