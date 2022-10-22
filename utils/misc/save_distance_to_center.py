from typing import List, Dict, Union
from loguru import logger


def save_distance(data_list: List[Dict]) -> Union[str, bool]:
    """ Сохранение нужного параметра с расстоянием отеля до центра города """

    for dict_data in data_list:
        if dict_data['label'] == 'Центр города' or dict_data['label'] == 'City center':
            distance_to_center = dict_data['distance']
            logger.info(f'distance найден: {distance_to_center}')
            return distance_to_center
    else:
        logger.error(f'distance не найден')
        return False
