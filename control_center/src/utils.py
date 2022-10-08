import requests, os


def parse_ip_range(ip_range):
    """Parse ip range to list of ips.

    Example:
        '192.1.1.0-20' is parsed to ['192.1.1.0', '192.1.1.1', ..., '192.1.1.20']
    """
    tmp, end = ip_range.split('-')
    base, start = tmp.rsplit('.', 1)
    start = int(start)
    end = int(end) + 1

    res = []
    for i in range(start, end):
        res.append(f'{base}.{i}')
    return res


def send_http_post(ip, payload):
    try:
        requests.post(ip, json=payload)
    except:
        pass


def ping_ip(ip_str, live_ips):
    cmd = ["ping", "-c 1 -W 0.3", ip_str]
    output = os.popen(" ".join(cmd)).readlines()

    flag = False
    for line in list(output):
        if not line:
            continue
        if str(line).upper().find("TTL") >= 0:
            flag = True
            break
    if flag:
        live_ips.append(ip_str)