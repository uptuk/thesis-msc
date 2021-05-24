# -*- coding: utf-8 -*-
import logging
from typing import Optional

import aiohttp


class GraphsenseSimpleAsync:
    def __init__(self, host: str, key: str, currency: str = 'btc', scheme: str = 'https', verify: bool = True) -> None:
        self.host = host
        self.headers = {'Accept': 'application/json', 'Authorization': key}
        self.currency = currency
        self.scheme = scheme

        self._session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=verify))

    async def close(self) -> None:
        return await self._session.close()

    async def __aenter__(self) -> 'GraphsenseSimpleAsync':
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> Optional[bool]:
        await self.close()
        return None

    async def _get(self, resource: str, params: dict = None) -> dict:
        if params is None:
            params = dict()
        url = f'{self.scheme}://{self.host}/{resource}'
        async with self._session.get(url, params=params, headers=self.headers, timeout=600) as response:
            return await response.json()

    async def get_tags(self) -> dict:
        return await self._get('tags')

    async def get_tags_taxonomies(self) -> dict:
        return await self._get('tags/taxonomies')

    async def get_tags_taxonomies_concepts(self, taxonomy: str) -> dict:
        return await self._get(f'tags/taxonomies/{taxonomy}/concepts')

    async def get_address_details(self, address: str) -> dict:
        return await self._get(f'{self.currency}/addresses/{address}')

    async def get_address_entity(self, address: str) -> dict:
        return await self._get(f'{self.currency}/addresses/{address}/entity')

    async def get_address_entity2(self, address: str) -> dict:
        try:
            entity = await self._get(f'{self.currency}/addresses/{address}/entity')
        except Exception as e:
            entity = {'error': str(e)}
        return {'address': address, 'entity': entity}

    async def get_address_links(self, address: str) -> dict:
        return await self._get(f'{self.currency}/addresses/{address}/links')

    async def get_address_directed_neighbors(self, address: str, direction: str = 'in') -> dict:
        if direction not in ['in', 'out']:
            raise ValueError('invalid direction')
        return await self._get(f'{self.currency}/addresses/{address}/neighbors', params={'direction': direction})

    async def get_address_directed_neighbors_w_origin(self, address: str, direction: str = 'in') -> dict:
        if direction not in ['in', 'out']:
            raise ValueError('invalid direction')
        neighbors = await self._get(f'{self.currency}/addresses/{address}/neighbors', params={'direction': direction})
        return {
            'origin': address,
            'neighbors': neighbors.get('neighbors', list())
        }

    async def get_address_neighbors(self, address: str) -> dict:
        neighbors = list()
        for direction in ['in', 'out']:
            directed_neighbors = await self.get_address_directed_neighbors(address, direction)
            neighbors.append(directed_neighbors.get('neighbors', list()))
        return {'neighbors': neighbors}

    async def get_address_tags(self, address: str) -> dict:
        return await self._get(f'{self.currency}/addresses/{address}/tags')

    async def get_address_txs(self, address: str) -> dict:
        return await self._get(f'{self.currency}/addresses/{address}/txs')

    async def get_entity(self, entity: int) -> dict:
        return await self._get(f'{self.currency}/entities/{entity}')

    async def get_entity_addresses(self, entity: int) -> dict:
        return await self._get(f'{self.currency}/entities/{entity}/addresses')

    async def get_entity_directed_neighbors2(self, entity: int, direction: str = 'in') -> dict:
        if direction not in ['in', 'out']:
            raise ValueError('invalid direction')
        neighbors = await self._get(f'{self.currency}/entities/{entity}/neighbors', params={'direction': direction})
        return {'entity': entity, 'neighbors': neighbors}

    async def get_entity_directed_neighbors(self, entity: int, direction: str = 'in') -> dict:
        if direction not in ['in', 'out']:
            raise ValueError('invalid direction')
        return await self._get(f'{self.currency}/entities/{entity}/neighbors', params={'direction': direction})

    async def get_entity_neighbors(self, entity: int) -> dict:
        neighbors = list()
        for direction in ['in', 'out']:
            directed_neighbors = await self.get_entity_directed_neighbors(entity, direction)
            neighbors.append(directed_neighbors.get('neighbors', list()))
        return {'neighbors': neighbors}

    async def get_entity_search(self, entity: int) -> dict:
        return await self._get(f'{self.currency}/entities/{entity}/search')

    async def get_entity_tags(self, entity: int) -> dict:
        return await self._get(f'{self.currency}/entities/{entity}/tags')

    async def get_rates(self, height: int) -> dict:
        return await self._get(f'{self.currency}/rates/{height}')

    async def get_txs(self) -> dict:
        return await self._get(f'{self.currency}/txs')

    async def get_tx_hash(self, tx_hash: str) -> dict:
        return await self._get(f'{self.currency}/txs/{tx_hash}')
