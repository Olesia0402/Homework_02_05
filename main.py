import asyncio
import logging
import pprint
import sys
from datetime import datetime, timedelta


from aiohttp import ClientSession, ClientConnectorError


URL_PB = 'https://api.privatbank.ua/p24api/exchange_rates?date='


async def request(url: str):
    async with ClientSession() as session:
        try:
            async with session.get(url) as resp:
                if resp.ok:
                    r = await resp.json()
                    return r
                logging.error(f"Error status: {resp.status} for {url}")
                return None
        except ClientConnectorError as err:
            logging.error(f"Connection error: {str(err)}")
            return None


def pb_handler(result):
    res = {}
    for currency in result['exchangeRate']:
        if currency['currency'] == 'EUR':
            res['EUR'] = {'sale': currency["saleRateNB"], 'purchase': currency["purchaseRateNB"]}
        elif currency['currency'] == 'USD':
            res['USD'] = {'sale': currency['saleRateNB'], 'purchase': currency['purchaseRateNB']}
    return {result["date"]: res}
   	

async def main(url, inx, handler):
    results = []
    if int(inx) < 10:
        list_of_date = [str((datetime.now() - timedelta(days=i)).strftime('%d.%m.%Y')) for i in range(int(inx))]
        list_of_urls = [(url + str(i)) for i in list_of_date]
        for url in list_of_urls:
            result = await request(url)
            if result:
                results.append(handler(result))
        return results
    else:
        return 'We can not show such period. Enter other.'

if __name__ == '__main__':
    try:
        if len(sys.argv) != 2:
            print("Usage: python script_name.py <number_of_days>")
            sys.exit(1)
        r = asyncio.run(main(URL_PB, sys.argv[1], pb_handler))
        pprint.pprint(r)
    except ValueError as err:
        logging.error(f"Error: {str(err)}. Please enter a valid number.")
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
