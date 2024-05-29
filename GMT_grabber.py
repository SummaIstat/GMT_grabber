from selenium.webdriver import Proxy
from Config import *
import logging_config
import os
import sys
import logging
import cv2
from random import randint
from time import sleep
from dataclasses import dataclass
from pyproj import Proj
from PIL import Image
from io import BytesIO
from os.path import expanduser
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

__author__ = "Donato Summa"

logging_config.setup_logger()
logger = logging.getLogger(__name__)
logger.debug(__name__ + ' logger initialized')
output_csv_file = ""
maps_folder = ""
negatives_folder = ""


@dataclass
class Point:
    """
    osm_id: str
    fclass: str
    name: str
    ref: str
    oneway: str
    bridge: str
    tunnel: str
    COD_RIP: str
    COD_REG: str
    COD_PROV: str
    PRO_COM: str
    COMUNE: str
    LOC2011: str
    ArcoMetri: str
    osm_id_1: str
    class_1: str
    name_1: str
    X_Pos: str
    Y_Pos: str
    """
    ID_INCIDENTE: str
    ANNO: str
    MESE: str
    GIORNO: str
    ORA: str
    MINUTI: str
    PROVIN: str
    COMUNE: str
    PROVCOM: str
    Longitudine: str
    Latitudine: str
    FERITI: str
    MORTI: str


def main(argv) -> None:


    # proxy = 'http://proxy.istat.it:3128'
    # localhost = 'http://127.0.0.1'
    # os.environ['no_proxy'] = localhost
    # os.environ['NO_PROXY'] = localhost
    # os.environ['http_proxy'] = proxy
    # os.environ['HTTP_PROXY'] = proxy
    # os.environ['https_proxy'] = proxy
    # os.environ['HTTPS_PROXY'] = proxy



    config = Config(argv)
    initialize_logger(config)
    global output_csv_file
    global maps_folder
    global negatives_folder

    file_date_time = datetime.now().strftime("%Y-%m-%d_%H_%M_%S")
    output_csv_file = str(config.OUTPUT_FOLDER_PATH) + "/" + str(config.PROGRAM_NAME) + "_" + str(file_date_time) + ".csv"
    write_header_on_output_file()

    maps_folder = str(config.MAPS_FOLDER_PATH) + "/"
    negatives_folder = str(config.NEGATIVES_FOLDER_PATH) + "/"
    point_list = get_point_list(config.INPUT_FILE_PATH)
    browser = get_browser()

    point: Point
    for point in point_list:
        logger.info(f"processing point {point.ID_INCIDENTE}")
        point.point_start_datetime = datetime.now().strftime("%Y-%m-%d_%H_%M_%S")
        # lat_long = get_transformed_coordinates(float(point.X_Pos), float(point.Y_Pos))
        lat_long = (float(point.Longitudine.replace(",", ".")), float(point.Latitudine.replace("," ,".")))
        zoom = 20
        point.url_map = 'https://www.google.it/maps/@' + str(lat_long[1]) + "," + str(lat_long[0]) + "," + str(zoom) + "z"
        point.url_traffic = 'https://www.google.it/maps/@' + str(lat_long[1]) + "," + str(lat_long[0]) + "," + str(zoom) + "z/data=!5m1!1e1"

        map_png = scrape(browser, str(point.url_map))
        traffic_png = scrape(browser, str(point.url_traffic))

        #map_png_path = save_image_on_disk(map_png, str(point.osm_id), config)
        map_png_path = save_image_on_disk(map_png, str(point.ID_INCIDENTE) + "_map")
        #traffic_png_path = save_image_on_disk(traffic_png, str(point.osm_id) + "_traffic")
        traffic_png_path = save_image_on_disk(traffic_png, str(point.ID_INCIDENTE) + "_traffic")

        img_map = cv2.imread(map_png_path)
        img_traffic = cv2.imread(traffic_png_path)
        diff = cv2.absdiff(img_map, img_traffic)
        mask = cv2.cvtColor(diff, cv2.IMREAD_COLOR)
        #path_diff_png = os.path.join(config.NEGATIVES_FOLDER_PATH, str(point.osm_id) + '.png')  # c:\\py\\traffic\\negativi\\3188829.png
        path_diff_png = os.path.join(config.NEGATIVES_FOLDER_PATH, str(point.ID_INCIDENTE) + '_neg.png')  # c:\\py\\traffic\\negativi\\3188829.png
        #path_diff_jpg = os.path.join(config.NEGATIVES_FOLDER_PATH, str(point.osm_id) + '.jpg')  # c:\\py\\traffic\\negativi\\3188829.jpg
        path_diff_jpg = os.path.join(config.NEGATIVES_FOLDER_PATH, str(point.ID_INCIDENTE) + '_neg.jpg')  # c:\\py\\traffic\\negativi\\3188829.jpg
        cv2.imwrite(path_diff_png, mask)
        im = Image.open(path_diff_png)
        rgb_im = im.convert('RGB')
        rgb_im.save(path_diff_jpg)
        point.traffic = get_traffic_from_image(path_diff_jpg)
        point.point_end_datetime = datetime.now().strftime("%Y-%m-%d_%H_%M_%S")
        append_line_on_output_file(point)

    browser.close()


# TODO: importare proxy dinamicamente da file di config
def get_browser():
    chrome_options = webdriver.ChromeOptions()

    # proxy_server_url = "http://proxy.istat.it:3128"
    # chrome_options.add_argument("--headless=new")
    # chrome_options.add_argument(f'--proxy-server={proxy_server_url}')

    # proxy = Proxy()
    # proxy.ftpProxy = "http://proxy.istat.it:3128"
    # proxy.httpProxy = "http://proxy.istat.it:3128"
    # proxy.sslProxy = "http://proxy.istat.it:3128"
    # chrome_options.set_capability("proxy", proxy)

    driver = webdriver.Chrome(
        service=ChromeService(ChromeDriverManager().install()),
        options=chrome_options
    )
    driver.maximize_window()
    return driver


def write_header_on_output_file():
    global output_csv_file
    with open(output_csv_file, 'a+') as f:
        header = "point_ID" + "\t" +\
                     "X_coord" + "\t" +\
                     "Y_coord" + "\t" +\
                     "start_datetime" + "\t" + \
                     "end_datetime" + "\t" + \
                     "traffic" + "\n"
        f.writelines(header)


def append_line_on_output_file(point: Point) -> None:
    global output_csv_file
    with open(output_csv_file, 'a+', encoding="utf-8") as f:
        """
        line_to_write = str(point.osm_id) + "\t" + \
                        str(point.X_Pos) + "\t" + \
                        str(point.Y_Pos) + "\t" + \
                        str(point.point_start_datetime) + "\t" + \
                        str(point.point_end_datetime) + "\t" + \
                        str(point.traffic) + "\n"
        """
        line_to_write = str(point.ID_INCIDENTE) + "\t" + \
                        str(point.Latitudine) + "\t" + \
                        str(point.Longitudine) + "\t" + \
                        str(point.point_start_datetime) + "\t" + \
                        str(point.point_end_datetime) + "\t" + \
                        str(point.traffic) + "\n"
        f.writelines(line_to_write)


def get_transformed_coordinates(coord_x: float, coord_y: float) -> tuple[float, float]:
    # performs cartographic transformations.
    # Converts from longitude, latitude to native map projection x,y coordinates and vice versa
    proj = Proj("+proj=utm +zone=32 +north +ellps=WGS84 +datum=WGS84 +units=m +no_defs")
    transformed_coordinates = proj(coord_x, coord_y, inverse=True)
    return transformed_coordinates


def save_image_on_disk(png_image_to_save, name) -> str:
    # Store image as bytes, crop it and save to desktop
    global maps_folder
    im = Image.open(BytesIO(png_image_to_save))
    width, height = im.size  # Get dimensions
    left = width / 4
    top = height / 4
    right = 4 * width / 5  # il 2 aumenta o diminuisce l'immagine se metto 3 aumenta
    bottom = 4 * height / 5  # il 2 aumenta o diminuisce l'immagine se metto 3 aumenta
    im = im.crop((left, top, right, bottom))
    #local_path = sys.path[0]
    #path0 = os.path.join(local_path, "maps/")
    #path = expanduser(path0)
    #im.save(path + name + '.png')
    im.save(maps_folder + name + '.png')
    # path_diff_png = os.path.join(config.MAPS_FOLDER_PATH, str(name) + '.png')  # c:\\py\\traffic\\negativi\\3188829.png
    #path_image = os.path.join(local_path, "maps", name + '.png')
    path_image = os.path.join(maps_folder, name + '.png')
    return path_image


# TODO: valore medio dei pixel non neri
def get_traffic_from_image(image_path):
    image = Image.open(image_path, 'r')
    pixel_values = list(image.getdata())
    green = []
    orange = []
    red = []
    dark = []
    black_pixels_count = 0
    r_value_count = 0
    g_value_count = 0
    b_value_count = 0
    for color in pixel_values:

        r_value_count = r_value_count + color[0]
        g_value_count = g_value_count + color[1]
        b_value_count = b_value_count + color[2]

        if (color[0] == 0) and (color[1] == 0) and (color[2] == 0):
            black_pixels_count = black_pixels_count + 1
        else:
            if (color[0] in range(60, 160)) and (color[1] in range(10, 70)) and (color[2] in range(20, 100)):
                green.append(color)
            if (color[0] in range(10, 50)) and (color[1] in range(60, 110)) and (color[2] in range(70, 120)):
                orange.append(color)
            if (color[0] in range(15, 80)) and (color[1] in range(130, 190)) and (color[2] in range(70, 240)):
                red.append(color)
            if (color[0] in range(90, 160)) and (color[1] in range(195, 255)) and (color[2] in range(120, 255)):
                dark.append(color)

    traffic = []
    if len(green) > 30:
        traffic.append(1)
    if len(orange) > 30:
        traffic.append(2)
    if len(red) > 30:
        traffic.append(3)
    if len(dark) > 30:
        traffic.append(4)
    if (len(green) < 30) and (len(orange) < 30) and (len(red) < 30) and (len(dark) < 30):
        traffic.append(0)

    non_black_pixels_count = len(pixel_values) - black_pixels_count
    r_mean_value = r_value_count / non_black_pixels_count
    g_mean_value = g_value_count / non_black_pixels_count
    b_mean_value = b_value_count / non_black_pixels_count

    return traffic


def scrape(browser, url_map):

    browser.get(url_map)
    try:
        pulsante_rifiuta = browser.find_element(By.XPATH, "//button[@aria-label='Rifiuta tutto']")
        if pulsante_rifiuta is not None:
            pulsante_rifiuta.click()
    except Exception:
        pass
    #sleep(2)  # just to be sure that the page is loaded
    secs_to_wait:int = randint(2, 7)
    sleep(secs_to_wait)
    png_image = browser.get_screenshot_as_png()
    return png_image


def initialize_logger(config) -> None:
    for h in logger.handlers:
        h.setLevel(logging.getLevelName(config.LOG_LEVEL))
    loggers = [logging.getLogger(name) for name in logging.root.manager.loggerDict]
    for log in loggers:
        log.setLevel(logging.getLevelName(config.LOG_LEVEL))
    logging.getLogger("pysolr").setLevel(logging.WARNING)
    logger.info("****************************************")
    logger.info("**********   GMT_grabber   *************")
    logger.info("****************************************\n\n")
    now = datetime.now()
    starting_date_time = now.strftime("%Y-%m-%d %H:%M:%S")
    logger.info("Starting datetime: " + starting_date_time)


def get_point_list(point_file_path: str) -> list[Point]:
    with open(point_file_path, "rt") as f:
        next(f)  # ignore the first line containing the header
        #field_separator: str = ","
        field_separator: str = "\t"
        #field_number: int = 19
        field_number: int = 13
        splitted_lines: list[list[str]] = [line.split(field_separator) for line in f.readlines()]
        point_list: list[Point] = []
        for tupla in splitted_lines:
            if len(tupla) == field_number:
                stripped_tuple = map(str.strip, tupla)
                point = Point(*stripped_tuple)
                point_list.append(point)
            else:
                logger.warning("The point " + str(tupla) + " is invalid and will not be considered !")
    return point_list


if __name__ == "__main__":
    main(sys.argv[1:])

# TODO: capire perchè a volte compaiono scritte e a volte no
# TODO: sistemare proxy da rete Istat
# TODO: individuare il pulsante "Rifiuta tutto" tramite label è poco robusto

