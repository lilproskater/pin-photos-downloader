from os.path import isfile as file_exists, isdir as directory_exists
from requests import get as requests_get
from os import mkdir, sep as os_sep
from re import sub as re_sub
from lxml import html


def modify_resolution(link, resolution):
    parts = link.split('/')
    return parts[0] + '//' + parts[2] + '/' + resolution + '/' + '/'.join(parts[4:])


# Enter URLS manually below, if you don't want to input file name with links after
urls = []
save_dir = ''
if not save_dir:
    print('Please configure save_dir (save directory)')
    exit()
if not directory_exists(save_dir):
    try:
        mkdir(save_dir)
    except PermissionError:
        print('Failed to create directory "' + save_dir + '". Permission denied')
        exit()

try:
    if not len(urls):
        f_name = input('Enter file name to read links from: ')
        if not file_exists(f_name):
            print('Error: File "' + f_name + '" does not exist!')
            exit()
        with open(f_name, 'r') as f:
            urls = [x.strip() for x in f.read().split('\n') if x]
    downloaded, urls_len = 0, len(urls)
    print('Number of URLs:' + str(urls_len))
    for url in urls:
        try:
            r = requests_get(url)
        except Exception:
            print('An error occurred with url: "' + url + '" check if URL is valid and accessible')
            continue
        tree = html.fromstring(r.text)
        elems = tree.xpath("//div[contains(@class, 'OVX')]//img[contains(@class, 'kVc')]")
        if not len(elems):
            print('No image found for url "' + url + '". Skipping...')
            continue
        src = modify_resolution(elems[0].attrib['src'], 'originals')
        ext = '.' + re_sub(r'\?.+', '', src.split('.')[-1])
        f_name = 'pin-' + url.split('/')[-1].rstrip('/') + ext
        resolutions = ('736x', '564x', '236x')  # If it cannot download originals it will try 736x, then 564x and so on
        for resolution in resolutions:
            img = requests_get(src)
            if img.status_code == 200:
                with open(save_dir + os_sep + f_name, 'wb') as f:
                    f.write(img.content)
                downloaded += 1
                print('Downloaded: (' + str(downloaded) + ' / ' + str(urls_len) + ')')
                break
            src = modify_resolution(src, resolution)
        else:
            print('Failed to download image for "' + url + '". Src: "' + src + '"')
except KeyboardInterrupt:
    print('\nGoodbye!')
