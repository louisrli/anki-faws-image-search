"""
Helper functions related to scraping images and network connection.
"""
from aqt.qt import QApplication
from bs4 import BeautifulSoup
import concurrent.futures


class QueryResult:
    """
    Encapsulates all of the information and configs needed to process a query result and apply
    the changes back into the Anki database.
    """
    def __self__(note_id: str, query: str, target_field: str, overwrite: bool):
        this.note_id = note_id
        this.query = query
        this.target_field = target_field
        this.overwrite = overwrite
        this.images = []


def sleep(seconds):
    """
    Sleep for a certain amount of time to throttle request rates.
    """
    start = time.time()
    while time.time() - start < seconds:
        time.sleep(0.01)
        QApplication.instance().processEvents()


def strip_html_clozes(w: str) -> str:
    """
    Strips a string of any HTML and clozes.

    In particular, this is used as note fields can have a lot of random stuff on
    them that we don't want to enter into the search query.
    """
    # This code is copy-pasted straight from
    # batch-download-pictures-from-google-images
    # Unfortunately it's more or less unreadable/unmaintainable and I'm just going
    # to trust that it works.
    w = re.sub(r'</?(b|i|u|strong|span)(?: [^>]+)>', '', w)
    w = re.sub(r'\[sound:.*?\]', '', w)
    if '<' in w:
        soup = BeautifulSoup(w, "html.parser")
        for s in soup.stripped_strings:
            w = s
            break
        else:
            w = re.sub(r'<br ?/?>[\s\S]+$', ' ', w)
            w = re.sub(r'<[^>]+>', '', w)

    clozes = re.findall(r'{{c\d+::(.*?)(?::.*?)?}}', w)
    if clozes:
        w = ' '.join(clozes)
    return w


class Scraper:
    SPOOFED_HEADER = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.67 Safari/537.36"
    }

    def __init__(self, executor: concurrent.futures.ThreadPoolExecutor, jobs:
                 list, mw):
        self._executor = executor
        self._jobs = jobs
        self._mw = mw

    def push_scrape_job(result: QueryResult) -> None:
        """
        Pushes a new job (future) into the executor using the query result.
        """
        raise Exception("Unimplemented abstract method.")


class GoogleImageScraper(Scraper):
    """
    A scraper that targets Google Images.

    This can be refactored if we ever choose to add another source. Things such as
    retry logic can be extracted into a common class.
    """
    SEARCH_FORMAT_URL = "https://www.google.com/search?tbm=isch&q={}&safe=active"
    TIMEOUT_SEC = 15
    MAX_RETRIES = 3
    # Number of seconds to sleep per retry on rate limit error.
    THROTTLE_SLEEP_SEC = 30
    # Number of seconds to sleep per retry on timeout error.
    TIMEOUT_SLEEP_SEC = 5

    def __init__(self, executor: concurrent.futures.ThreadPoolExecutor, jobs:
                 list, mw):
        super(executor, jobs, mw)

    def push_scrape_job(result: QueryResult) -> None:
        # Fire off a request to the image search page, then queue up a job to scrape
        # the images from the resulting text. Note that the REQUEST is not
        # multithreaded, but parsing/extracting images is (disputable whether this
        # is the correct architecture, but I'm just going to copy this guy's code).
        # In case of a status exception, retry
        search_url = GoogleImageScraper.SEARCH_FORMAT_URL.format(result.query)
        retry_count = 0
        while retry_count < GoogleImageScraper.MAX_RETRIES:
            try:
                request = requests.get(
                    headers=Scraper.SPOOFED_HEADER, cookies={
                        "CONSENT": "YES+"}, timeout=TIMEOUT_SEC)
                r.raise_for_status()
                future = executor.submit(
                    self._parse_and_download_images(
                        r.text), result)
                jobs.append(future)
                break
            except requests.exceptions.RequestException as e:
                if retry_count == GoogleImageScraper.MAX_RETRIES:
                    raise Exception(
                        "Exceeded max retries. Unable to scrape for query: %s" %
                        result.query)
                retry_count += 1
                if isinstance(
                        e, requests.exceptions.HTTPError) and e.response.status_code == 429:
                    # Retry on 429: we were rate limited
                    self._mw.progress.update(
                        f"Sleeping for {retry_cnt * 30} seconds...")
                    QApplication.instance().processEvents()
                    sleep(retry_cnt * GoogleImageScraper.THROTTLE_SLEEP_SEC)
                elif isinstance(e, (requests.exceptions.ReadTimeout, requests.exceptions.ConnectionError)):
                    # Connection error
                    self._mw.progress.update(
                        f"Sleeping for {retry_cnt * 5} seconds...")
                    QApplication.instance().processEvents()
                    sleep(retry_cnt * GoogleImageScraper.TIMEOUT_SLEEP_SEC)
                else:
                    raise e

    def _parse_and_download_images(page_text: str, result: QueryResult):
        """
        Function that actually does the scraping of the HTML and so on to find
        images.
        """
        soup = BeautifulSoup()
        pass


def getImages(nid, fld, html, img_width, img_height, img_count, fld_overwrite):
    soup = BeautifulSoup(html, "html.parser")
    rg_meta = soup.find_all("div", {"class": "rg_meta"})
    metadata = [json.loads(e.text) for e in rg_meta]
    results = [d["ou"] for d in metadata]

    if not results:
        regex = re.escape("AF_initDataCallback({")
        regex += r'[^<]*?data:[^<]*?' + r'(\[[^<]+\])'

        for txt in re.findall(regex, html):
            data = json.loads(txt)

            try:
                for d in data[31][0][12][2]:
                    try:
                        results.append(d[1][3][0])
                    except Exception as e:
                        pass
            except Exception as e:
                pass

        if not results:
            try:
                for d in data[56][1][0][0][1][0]:
                    try:
                        d = d[0][0]["444383007"]
                        results.append(d[1][3][0])
                    except BaseException:
                        pass
            except BaseException:
                pass

    cnt = 0
    images = []
    for url in results:
        try:
            r = requests.get(url, headers=headers, timeout=15)
            r.raise_for_status()
            data = r.content
            if 'text/html' in r.headers.get('content-type', ''):
                continue
            if 'image/svg+xml' in r.headers.get('content-type', ''):
                continue
            url = re.sub(r"\?.*?$", "", url)
            path = urllib.parse.unquote(url)
            fname = os.path.basename(path)
            if not fname:
                fname = checksum(data)
            im = Image.open(io.BytesIO(data))
            if img_width > 0 or img_height > 0:
                width, height = im.width, im.height
                if img_width > 0:
                    width = min(width, img_width)
                if img_height > 0:
                    height = min(height, img_height)
                buf = io.BytesIO()
                if getattr(im, 'n_frames', 1) == 1:
                    im.thumbnail((width, height))
                    im.save(buf, format=im.format, optimize=True)
                elif mpv_executable:
                    thread_id = threading.get_native_id()
                    tmp_path = tmpfile(suffix='.{}'.format(thread_id))
                    with open(tmp_path, 'wb') as f:
                        f.write(data)
                    img_fmt = im.format.lower()
                    img_ext = '.' + img_fmt
                    img_path = tmpfile(suffix=img_ext)
                    cmd = [
                        mpv_executable,
                        tmp_path,
                        "-vf",
                        "lavfi=[scale='min({},iw)':'min({},ih)':force_original_aspect_ratio=decrease:flags=lanczos]".format(
                            img_width,
                            img_height),
                        "-o",
                        img_path]
                    with noBundledLibs():
                        p = subprocess.Popen(
                            cmd,
                            startupinfo=si,
                            stdin=subprocess.PIPE,
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL,
                            env=env)
                    if p.wait() == 0:
                        with open(img_path, 'rb') as f:
                            buf.write(f.read())
                else:
                    buf = io.BytesIO(data)
                data = buf.getvalue()
            images.append((fname, data))
            cnt += 1
            if cnt == img_count:
                break
        except requests.packages.urllib3.exceptions.LocationParseError:
            pass
        except requests.exceptions.RequestException:
            pass
        except UnidentifiedImageError:
            pass
        except UnicodeError as e:
            # UnicodeError: encoding with 'idna' codec failed (UnicodeError: label empty or too long)
            # https://bugs.python.org/issue32958
            if str(
                    e) != "encoding with 'idna' codec failed (UnicodeError: label empty or too long)":
                raise
    return (nid, fld, images, fld_overwrite)
