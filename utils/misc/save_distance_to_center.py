import re
from typing import List, Dict, Union
from loguru import logger


def save_distance(data_list: List[Dict]) -> Union[float, bool]:
    """ Сохранение нужного параметра с расстоянием отеля до центра города """

    pattern = r'(\d*)'

    for dict_data in data_list:
        if dict_data['label'] == 'Центр города' or dict_data['label'] == 'City center':
            find = re.match(pattern, dict_data['distance'])
            if find:
                distance_to_center = find.group(1).replace(',', '.')
                distance_to_center = float(distance_to_center)
                logger.info(f'distance найден: {distance_to_center}')

                return distance_to_center

            logger.error('Ошибка при конвертации параметра')
    else:
        logger.error(f'distance не найден')
        return False
