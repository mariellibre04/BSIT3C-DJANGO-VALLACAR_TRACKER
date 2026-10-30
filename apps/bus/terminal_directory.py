"""Directory of bus terminal locations served by Vallacar Transit.

The terminal monitor kiosk uses this catalogue for its sidebar so a display
can be locked to one terminal location and only show that terminal's
movements and available buses. The local Negros Occidental/Negros Oriental
coverage is kept for everyday operations, while every terminal Vallacar owns
nationwide is merged in from the terminal master list.
"""

import json
import re
import unicodedata
from pathlib import Path

from .route_config import TERMINAL_MASTER_LIST

_CITY_DATA_PATH = Path(__file__).with_name('data') / 'ph_cities.json'

_DROP_TOKENS = {
    'terminal', 'terminals', 'bus', 'buses', 'integrated', 'exchange',
    'grand', 'central', 'city', 'inc', 'corp', 'co', 'the', 'and', 'ng',
}


def normalize_name(value):
    """Lowercase, strip accents/punctuation and drop generic terminal words."""
    text = unicodedata.normalize('NFKD', (value or '').lower())
    text = ''.join(char for char in text if not unicodedata.combining(char))
    text = text.replace('&', ' and ')
    tokens = [token for token in re.findall(r'[a-z0-9]+', text) if token]
    meaningful = [token for token in tokens if token not in _DROP_TOKENS]
    return ' '.join(meaningful or tokens)


def _token_subset(needle, haystack):
    needle_tokens = needle.split()
    if not needle_tokens:
        return False
    haystack_tokens = set(haystack.split())
    return all(token in haystack_tokens for token in needle_tokens)


def _slug(value):
    return re.sub(r'[^a-z0-9]+', '-', (value or '').lower()).strip('-')


def _load_cities():
    try:
        rows = json.loads(_CITY_DATA_PATH.read_text(encoding='utf-8'))
    except (OSError, ValueError):
        return []
    return rows


_CITIES = _load_cities()

# The bundled city dataset covers most municipalities but not every city.
# These coordinates come from the Vallacar route terminal list.
_COORDINATE_OVERRIDES = {
    'baliwag': (14.9540, 120.8960),
    'bacolod': (10.6765, 122.9509),
    'san jose de buenavista': (10.7450, 121.9410),
    'victorias': (10.9000, 123.0667),
    'kabankalan': (9.9917, 122.8128),
    'sipalay': (9.7500, 122.4000),
    'hinigaran': (10.0417, 122.8567),
    'san carlos': (10.4966, 123.4224),
    'cadiz': (10.9586, 123.1321),
    'sagay': (10.8917, 123.4150),
    'escalante': (10.8333, 123.5000),
    'binalbagan': (10.0739, 122.8667),
    'himamaylan': (10.1003, 122.8702),
    'la carlota': (10.4167, 122.9167),
    'cebu': (10.3157, 123.8854),
    'dumaguete': (9.3072, 123.3080),
    'mabinay': (9.7264, 122.9256),
    'bais': (9.5917, 123.1222),
    'tanjay': (9.5167, 123.1583),
    'bayawan': (9.3667, 122.8000),
    'canlaon': (10.3833, 123.2000),
    'guihulngan': (10.1167, 123.2667),
}


def _city_coordinates(city, province):
    override = _COORDINATE_OVERRIDES.get(normalize_name(city))
    if override is not None:
        return override
    city_norm = (city or '').strip().lower()
    province_norm = (province or '').strip().lower()
    variants = {city_norm}
    if city_norm.endswith(' city'):
        variants.add(city_norm[:-5].strip())
    else:
        variants.add(f'{city_norm} city')

    fallback = None
    for row in _CITIES:
        name_norm = (row.get('name') or '').strip().lower()
        if name_norm not in variants:
            continue
        if province_norm and (row.get('province') or '').strip().lower() == province_norm:
            return row.get('lat'), row.get('lng')
        if fallback is None:
            fallback = row
    if fallback is not None:
        return fallback.get('lat'), fallback.get('lng')
    return None, None


def _seed(city, province, terminal, slug, aliases=(), hub=False,
          featured=False, lat=None, lng=None, region='', island=''):
    if lat is None or lng is None:
        found_lat, found_lng = _city_coordinates(city, province)
        lat = found_lat if lat is None else lat
        lng = found_lng if lng is None else lng
    display_city = (city or '').strip()
    if display_city.lower().endswith(' city'):
        display_city = display_city[:-5].strip()
    match_names = {city, display_city, terminal, *aliases}
    return {
        'slug': slug,
        'name': display_city or terminal,
        'city': city,
        'terminal': terminal,
        'province': province,
        'region': region,
        'island': island,
        'lat': lat,
        'lng': lng,
        'hub': hub,
        'featured': featured,
        'aliases': tuple(aliases),
        'match_keys': tuple(
            key for key in (normalize_name(name) for name in match_names) if key
        ),
    }


_PROVINCE_META = {
    'Metro Manila': ('NCR', 'Luzon'),
    'Batangas': ('Region IV-A', 'Luzon'),
    'Cebu': ('Region VII', 'Visayas'),
    'Aklan': ('Region VI', 'Visayas'),
    'Iloilo': ('Region VI', 'Visayas'),
    'Negros Occidental': ('Region VI', 'Negros Island'),
    'Negros Oriental': ('Region VII', 'Negros Island'),
}


# Region groups are ordered north to south so the sidebar reads like a
# nationwide terminal directory. Each group is a Philippine administrative
# region; the bus terminal seeds are the major terminals riders can pick from.
REGION_SEEDS = [
    {
        'region': 'NCR', 'island': 'Luzon',
        'terminals': [
            _seed('Quezon City', 'Metro Manila', 'Cubao Bus Terminal', 'cubao',
                  aliases=('Cubao', 'Araneta City Bus Terminal', 'Araneta'),
                  hub=True, featured=True, lat=14.6197, lng=121.0530),
            _seed('Quezon City', 'Metro Manila', 'Araneta City Bus Port', 'araneta-city',
                  aliases=('Araneta City Bus Port', 'Araneta City'), lat=14.6205, lng=121.0535),
            _seed('Pasay', 'Metro Manila', 'Parañaque Integrated Terminal Exchange', 'pitx',
                  aliases=('PITX', 'Parañaque', 'Paranaque', 'Pasay'),
                  hub=True, featured=True, lat=14.5106, lng=120.9918),
            _seed('Makati', 'Metro Manila', 'Buendia Bus Terminal', 'buendia',
                  aliases=('Buendia', 'Gil Puyat'), lat=14.5547, lng=121.0244),
            _seed('Manila', 'Metro Manila', 'Sampaloc Bus Terminal', 'sampaloc',
                  aliases=('Sampaloc', 'Manila'), lat=14.6091, lng=120.9891),
            _seed('Caloocan City', 'Metro Manila', 'Caloocan Bus Terminal', 'caloocan',
                  lat=14.6571, lng=120.9830),
            _seed('Muntinlupa City', 'Metro Manila', 'Alabang Bus Terminal', 'alabang',
                  aliases=('Alabang',), lat=14.4200, lng=121.0450),
            _seed('Valenzuela City', 'Metro Manila', 'Valenzuela Bus Terminal', 'valenzuela',
                  lat=14.7011, lng=120.9830),
        ],
    },
    {
        'region': 'CAR', 'island': 'Luzon',
        'terminals': [
            _seed('Baguio City', 'Benguet', 'Baguio Bus Terminal', 'baguio',
                  aliases=('Baguio', 'Governor Pack Road'), hub=True, featured=True),
            _seed('Bangued', 'Abra', 'Abra Bus Terminal', 'bangued', aliases=('Abra',)),
            _seed('Tabuk City', 'Kalinga', 'Kalinga Bus Terminal', 'tabuk',
                  aliases=('Tabuk', 'Kalinga')),
            _seed('Bontoc', 'Mountain Province', 'Mountain Province Bus Terminal', 'bontoc'),
            _seed('Lagawe', 'Ifugao', 'Ifugao Bus Terminal', 'lagawe'),
            _seed('Kabugao', 'Apayao', 'Apayao Bus Terminal', 'kabugao'),
        ],
    },
    {
        'region': 'Region I', 'island': 'Luzon',
        'terminals': [
            _seed('Laoag City', 'Ilocos Norte', 'Ilocos Norte Bus Terminal', 'laoag',
                  aliases=('Laoag',)),
            _seed('Vigan City', 'Ilocos Sur', 'Vigan Bus Terminal', 'vigan', aliases=('Vigan',)),
            _seed('Candon City', 'Ilocos Sur', 'Candon Bus Terminal', 'candon', aliases=('Candon',)),
            _seed('Dagupan City', 'Pangasinan', 'Dagupan Bus Terminal', 'dagupan', aliases=('Dagupan',)),
            _seed('Urdaneta City', 'Pangasinan', 'Urdaneta Bus Terminal', 'urdaneta', aliases=('Urdaneta',)),
            _seed('San Fernando City', 'La Union', 'San Fernando Bus Terminal', 'san-fernando-la-union',
                  aliases=('San Fernando La Union',)),
            _seed('Alaminos City', 'Pangasinan', 'Alaminos Bus Terminal', 'alaminos', aliases=('Alaminos',)),
            _seed('Lingayen', 'Pangasinan', 'Lingayen Bus Terminal', 'lingayen', aliases=('Lingayen',)),
            _seed('Batac City', 'Ilocos Norte', 'Batac Bus Terminal', 'batac', aliases=('Batac',)),
        ],
    },
    {
        'region': 'Region II', 'island': 'Luzon',
        'terminals': [
            _seed('Tuguegarao City', 'Cagayan', 'Tuguegarao Bus Terminal', 'tuguegarao',
                  aliases=('Tuguegarao',)),
            _seed('Ilagan City', 'Isabela', 'Ilagan Bus Terminal', 'ilagan', aliases=('Ilagan',)),
            _seed('Cauayan City', 'Isabela', 'Cauayan Bus Terminal', 'cauayan', aliases=('Cauayan',)),
            _seed('Santiago City', 'Isabela', 'Santiago Bus Terminal', 'santiago', aliases=('Santiago',)),
            _seed('Bayombong', 'Nueva Vizcaya', 'Nueva Vizcaya Bus Terminal', 'bayombong'),
            _seed('Basco', 'Batanes', 'Batanes Bus Terminal', 'basco', aliases=('Batanes',)),
        ],
    },
    {
        'region': 'Region III', 'island': 'Luzon',
        'terminals': [
            _seed('Angeles City', 'Pampanga', 'Angeles Bus Terminal', 'angeles',
                  aliases=('Angeles',)),
            _seed('San Fernando City', 'Pampanga', 'San Fernando Bus Terminal', 'san-fernando-pampanga',
                  aliases=('San Fernando Pampanga',)),
            _seed('Olongapo City', 'Zambales', 'Olongapo Bus Terminal', 'olongapo',
                  aliases=('Olongapo',)),
            _seed('Balanga City', 'Bataan', 'Balanga Bus Terminal', 'balanga', aliases=('Balanga',)),
            _seed('Cabanatuan City', 'Nueva Ecija', 'Cabanatuan Bus Terminal', 'cabanatuan',
                  aliases=('Cabanatuan',)),
            _seed('Tarlac City', 'Tarlac', 'Tarlac Bus Terminal', 'tarlac', aliases=('Tarlac',)),
            _seed('Malolos City', 'Bulacan', 'Malolos Bus Terminal', 'malolos', aliases=('Malolos',)),
            _seed('San Jose City', 'Nueva Ecija', 'San Jose Bus Terminal', 'san-jose-nueva-ecija',
                  aliases=('San Jose Nueva Ecija',)),
            _seed('Gapan City', 'Nueva Ecija', 'Gapan Bus Terminal', 'gapan', aliases=('Gapan',)),
            _seed('Iba', 'Zambales', 'Zambales Bus Terminal', 'iba-zambales', aliases=('Iba Zambales',)),
            _seed('Baliwag', 'Bulacan', 'Baliwag Bus Terminal', 'baliwag', aliases=('Baliwag',)),
        ],
    },
    {
        'region': 'Region IV-A', 'island': 'Luzon',
        'terminals': [
            _seed('Batangas City', 'Batangas', 'Batangas Grand Terminal', 'batangas',
                  aliases=('Batangas', 'Batangas Grand Terminal')),
            _seed('Lucena City', 'Quezon', 'Lucena Grand Terminal', 'lucena', aliases=('Lucena',)),
            _seed('Antipolo City', 'Rizal', 'Antipolo Bus Terminal', 'antipolo', aliases=('Antipolo',)),
            _seed('Calamba City', 'Laguna', 'Calamba Bus Terminal', 'calamba', aliases=('Calamba',)),
            _seed('Santa Rosa City', 'Laguna', 'Santa Rosa Bus Terminal', 'santa-rosa',
                  aliases=('Santa Rosa',)),
            _seed('Tagaytay City', 'Cavite', 'Tagaytay Bus Terminal', 'tagaytay', aliases=('Tagaytay',)),
            _seed('Lipa City', 'Batangas', 'Lipa Bus Terminal', 'lipa', aliases=('Lipa',)),
            _seed('Tanauan City', 'Batangas', 'Tanauan Bus Terminal', 'tanauan', aliases=('Tanauan',)),
            _seed('Lucban', 'Quezon', 'Lucban Bus Terminal', 'lucban', aliases=('Lucban',)),
            _seed('Infanta', 'Quezon', 'Infanta Bus Terminal', 'infanta', aliases=('Infanta',)),
            _seed('Santa Cruz', 'Laguna', 'Santa Cruz Bus Terminal', 'santa-cruz-laguna',
                  aliases=('Santa Cruz Laguna',)),
            _seed('Gumaca', 'Quezon', 'Gumaca Bus Terminal', 'gumaca', aliases=('Gumaca',)),
        ],
    },
    {
        'region': 'MIMAROPA', 'island': 'Luzon',
        'terminals': [
            _seed('Calapan City', 'Oriental Mindoro', 'Calapan Bus Terminal', 'calapan',
                  aliases=('Calapan',)),
            _seed('Puerto Princesa City', 'Palawan', 'Puerto Princesa Bus Terminal', 'puerto-princesa',
                  aliases=('Puerto Princesa',)),
            _seed('San Jose', 'Occidental Mindoro', 'San Jose Bus Terminal', 'san-jose-occidental-mindoro',
                  aliases=('San Jose Occidental Mindoro',)),
            _seed('Mamburao', 'Occidental Mindoro', 'Mamburao Bus Terminal', 'mamburao',
                  aliases=('Mamburao',)),
            _seed('Boac', 'Marinduque', 'Marinduque Bus Terminal', 'boac', aliases=('Boac', 'Marinduque')),
            _seed('Romblon', 'Romblon', 'Romblon Bus Terminal', 'romblon', aliases=('Romblon',)),
            _seed('Odiongan', 'Romblon', 'Odiongan Bus Terminal', 'odiongan', aliases=('Odiongan',)),
            _seed('Coron', 'Palawan', 'Coron Bus Terminal', 'coron', aliases=('Coron',)),
            _seed('El Nido', 'Palawan', 'El Nido Bus Terminal', 'el-nido', aliases=('El Nido',)),
        ],
    },
    {
        'region': 'Region V', 'island': 'Luzon',
        'terminals': [
            _seed('Naga City', 'Camarines Sur', 'Naga Bus Terminal', 'naga-camarines-sur',
                  aliases=('Naga', 'Naga Camarines Sur')),
            _seed('Legazpi City', 'Albay', 'Legazpi Bus Terminal', 'legazpi', aliases=('Legazpi',)),
            _seed('Sorsogon City', 'Sorsogon', 'Sorsogon Bus Terminal', 'sorsogon', aliases=('Sorsogon',)),
            _seed('Daet', 'Camarines Norte', 'Daet Bus Terminal', 'daet', aliases=('Daet',)),
            _seed('Iriga City', 'Camarines Sur', 'Iriga Bus Terminal', 'iriga', aliases=('Iriga',)),
            _seed('Tabaco City', 'Albay', 'Tabaco Bus Terminal', 'tabaco', aliases=('Tabaco',)),
            _seed('Masbate City', 'Masbate', 'Masbate Bus Terminal', 'masbate', aliases=('Masbate',)),
            _seed('Virac', 'Catanduanes', 'Virac Bus Terminal', 'virac', aliases=('Virac',)),
            _seed('Pili', 'Camarines Sur', 'Pili Bus Terminal', 'pili', aliases=('Pili',)),
        ],
    },
    {
        'region': 'Region VI', 'island': 'Visayas',
        'terminals': [
            _seed('Iloilo City', 'Iloilo', 'Iloilo Bus Terminal', 'iloilo',
                  aliases=('Iloilo', 'Tagbak', 'Molo'), hub=True, featured=True),
            _seed('Bacolod City', 'Negros Occidental', 'Bacolod North Bus Terminal', 'bacolod-north',
                  aliases=('Bacolod', 'Bacolod North'), hub=True, featured=True),
            _seed('Bacolod City', 'Negros Occidental', 'Bacolod South Bus Terminal', 'bacolod-south',
                  aliases=('Bacolod South',), featured=True),
            _seed('Roxas City', 'Capiz', 'Roxas Bus Terminal', 'roxas-capiz',
                  aliases=('Roxas City', 'Roxas Capiz')),
            _seed('Kalibo', 'Aklan', 'Kalibo Bus Terminal', 'kalibo', aliases=('Kalibo',)),
            _seed('San Jose de Buenavista', 'Antique', 'Antique Bus Terminal', 'san-jose-antique',
                  aliases=('San Jose Antique', 'Antique')),
            _seed('Jordan', 'Guimaras', 'Guimaras Bus Terminal', 'jordan-guimaras',
                  aliases=('Guimaras', 'Jordan')),
            _seed('Passi City', 'Iloilo', 'Passi Bus Terminal', 'passi', aliases=('Passi',)),
            _seed('Victorias City', 'Negros Occidental', 'Victorias Bus Terminal', 'victorias',
                  aliases=('Victorias',), featured=True),
            _seed('Kabankalan City', 'Negros Occidental', 'Kabankalan Bus Terminal', 'kabankalan',
                  aliases=('Kabankalan', 'Kabnakalan'), hub=True, featured=True),
            _seed('Sipalay City', 'Negros Occidental', 'Sipalay Bus Terminal', 'sipalay',
                  aliases=('Sipalay',), featured=True),
            _seed('Hinigaran', 'Negros Occidental', 'Hinigaran Bus Terminal', 'hinigaran',
                  aliases=('Hinigaran',)),
            _seed('San Carlos City', 'Negros Occidental', 'San Carlos Bus Terminal', 'san-carlos',
                  aliases=('San Carlos',), featured=True),
            _seed('Cadiz City', 'Negros Occidental', 'Cadiz Bus Terminal', 'cadiz', aliases=('Cadiz',)),
            _seed('Sagay City', 'Negros Occidental', 'Sagay Bus Terminal', 'sagay', aliases=('Sagay',)),
            _seed('Escalante City', 'Negros Occidental', 'Escalante Bus Terminal', 'escalante',
                  aliases=('Escalante',)),
            _seed('Binalbagan', 'Negros Occidental', 'Binalbagan Bus Terminal', 'binalbagan',
                  aliases=('Binalbagan',)),
            _seed('Himamaylan City', 'Negros Occidental', 'Himamaylan Bus Terminal', 'himamaylan',
                  aliases=('Himamaylan',)),
            _seed('La Carlota City', 'Negros Occidental', 'La Carlota Bus Terminal', 'la-carlota',
                  aliases=('La Carlota',)),
            _seed('Bago City', 'Negros Occidental', 'Bago Bus Terminal', 'bago', aliases=('Bago',)),
            _seed('Silay City', 'Negros Occidental', 'Silay Bus Terminal', 'silay', aliases=('Silay',)),
            _seed('Talisay City', 'Negros Occidental', 'Talisay Bus Terminal', 'talisay-negros',
                  aliases=('Talisay Negros',)),
            _seed('Murcia', 'Negros Occidental', 'Murcia Bus Terminal', 'murcia', aliases=('Murcia',)),
            _seed('Salvador Benedicto', 'Negros Occidental', 'Don Salvador Benedicto Bus Terminal',
                  'salvador-benedicto', aliases=('Don Salvador Benedicto',)),
            _seed('Calatrava', 'Negros Occidental', 'Calatrava Bus Terminal', 'calatrava',
                  aliases=('Calatrava',)),
            _seed('Toboso', 'Negros Occidental', 'Toboso Bus Terminal', 'toboso', aliases=('Toboso',)),
            _seed('Manapla', 'Negros Occidental', 'Manapla Bus Terminal', 'manapla', aliases=('Manapla',)),
            _seed('Enrique B. Magalona', 'Negros Occidental', 'Enrique B. Magalona Bus Terminal',
                  'enrique-b-magalona', aliases=('Saravia', 'E.B. Magalona')),
            _seed('Valladolid', 'Negros Occidental', 'Valladolid Bus Terminal', 'valladolid',
                  aliases=('Valladolid',)),
            _seed('Pulupandan', 'Negros Occidental', 'Pulupandan Bus Terminal', 'pulupandan',
                  aliases=('Pulupandan',)),
            _seed('Pontevedra', 'Negros Occidental', 'Pontevedra Bus Terminal', 'pontevedra',
                  aliases=('Pontevedra',)),
            _seed('San Enrique', 'Negros Occidental', 'San Enrique Bus Terminal', 'san-enrique',
                  aliases=('San Enrique',)),
            _seed('La Castellana', 'Negros Occidental', 'La Castellana Bus Terminal', 'la-castellana',
                  aliases=('La Castellana',)),
            _seed('Moises Padilla', 'Negros Occidental', 'Moises Padilla Bus Terminal', 'moises-padilla',
                  aliases=('Moises Padilla',)),
            _seed('Isabela', 'Negros Occidental', 'Isabela Bus Terminal', 'isabela-negros',
                  aliases=('Isabela Negros',)),
            _seed('Ilog', 'Negros Occidental', 'Ilog Bus Terminal', 'ilog', aliases=('Ilog',)),
            _seed('Cauayan', 'Negros Occidental', 'Cauayan Bus Terminal', 'cauayan-negros',
                  aliases=('Cauayan Negros',)),
            _seed('Candoni', 'Negros Occidental', 'Candoni Bus Terminal', 'candoni', aliases=('Candoni',)),
            _seed('Hinoba-an', 'Negros Occidental', 'Hinoba-an Bus Terminal', 'hinoba-an',
                  aliases=('Hinobaan',)),
        ],
    },
    {
        'region': 'Region VII', 'island': 'Visayas',
        'terminals': [
            _seed('Cebu City', 'Cebu', 'Cebu South Bus Terminal', 'cebu-south',
                  aliases=('Cebu', 'CEBU-SOUTH', 'Cebu South'), hub=True, featured=True),
            _seed('Cebu City', 'Cebu', 'Cebu North Bus Terminal', 'cebu-north',
                  aliases=('Cebu North',)),
            _seed('Mandaue City', 'Cebu', 'Mandaue Bus Terminal', 'mandaue', aliases=('Mandaue',)),
            _seed('Lapu-Lapu City', 'Cebu', 'Lapu-Lapu Bus Terminal', 'lapu-lapu',
                  aliases=('Lapu-Lapu',)),
            _seed('Danao City', 'Cebu', 'Danao Bus Terminal', 'danao', aliases=('Danao',)),
            _seed('Bogo City', 'Cebu', 'Bogo Bus Terminal', 'bogo', aliases=('Bogo',)),
            _seed('Toledo City', 'Cebu', 'Toledo Bus Terminal', 'toledo', aliases=('Toledo',)),
            _seed('Carcar City', 'Cebu', 'Carcar Bus Terminal', 'carcar', aliases=('Carcar',)),
            _seed('Argao', 'Cebu', 'Argao Bus Terminal', 'argao', aliases=('Argao',)),
            _seed('Oslob', 'Cebu', 'Oslob Bus Terminal', 'oslob', aliases=('Oslob',)),
            _seed('Talisay City', 'Cebu', 'Talisay Cebu Bus Stop', 'talisay-cebu',
                  aliases=('Talisay Cebu', 'Talisay (Cebu)'), lat=10.2447, lng=123.8494),
            _seed('Minglanilla', 'Cebu', 'Minglanilla Bus Stop', 'minglanilla',
                  aliases=('Minglanilla',), lat=10.2444, lng=123.7964),
            _seed('City of Naga', 'Cebu', 'Naga Cebu Bus Stop', 'naga-cebu',
                  aliases=('Naga Cebu', 'Naga (Cebu)'), lat=10.2089, lng=123.7581),
            _seed('San Fernando', 'Cebu', 'San Fernando Cebu Bus Stop', 'san-fernando-cebu',
                  aliases=('San Fernando Cebu', 'San Fernando (Cebu)'),
                  lat=10.1622, lng=123.7075),
            _seed('Sibonga', 'Cebu', 'Sibonga Bus Stop', 'sibonga',
                  aliases=('Sibonga', 'Simala'), lat=10.0167, lng=123.6167),
            _seed('Dalaguete', 'Cebu', 'Dalaguete Bus Stop', 'dalaguete',
                  aliases=('Dalaguete',), lat=9.7611, lng=123.5347),
            _seed('Alcoy', 'Cebu', 'Alcoy Bus Stop', 'alcoy',
                  aliases=('Alcoy',), lat=9.7086, lng=123.5069),
            _seed('Boljoon', 'Cebu', 'Boljoon Bus Stop', 'boljoon',
                  aliases=('Boljoon',), lat=9.6289, lng=123.4786),
            _seed('Santander', 'Cebu', 'Santander Bus Stop', 'santander',
                  aliases=('Santander', 'Liloan Port'), lat=9.4167, lng=123.3333),
            _seed('Moalboal', 'Cebu', 'Moalboal Bus Terminal', 'moalboal', aliases=('Moalboal',)),
            _seed('Bato', 'Cebu', 'Bato Bus Terminal', 'bato-cebu', aliases=('Bato Cebu',)),
            _seed('Samboan', 'Cebu', 'Samboan Bus Terminal', 'samboan', aliases=('Samboan',)),
            _seed('Tagbilaran City', 'Bohol', 'Tagbilaran Bus Terminal', 'tagbilaran',
                  aliases=('Tagbilaran', 'Bohol')),
            _seed('Talibon', 'Bohol', 'Talibon Bus Terminal', 'talibon', aliases=('Talibon',)),
            _seed('Ubay', 'Bohol', 'Ubay Bus Terminal', 'ubay', aliases=('Ubay',)),
            _seed('Carmen', 'Bohol', 'Carmen Bus Terminal', 'carmen-bohol',
                  aliases=('Carmen Bohol',)),
            _seed('Tubigon', 'Bohol', 'Tubigon Bus Terminal', 'tubigon', aliases=('Tubigon',)),
            _seed('Dumaguete City', 'Negros Oriental', 'Dumaguete Bus Terminal', 'dumaguete',
                  aliases=('Dumaguete',), hub=True, featured=True),
            _seed('Mabinay', 'Negros Oriental', 'Mabinay Bus Terminal', 'mabinay',
                  aliases=('Mabinay',)),
            _seed('Bais City', 'Negros Oriental', 'Bais Bus Terminal', 'bais', aliases=('Bais',)),
            _seed('Tanjay City', 'Negros Oriental', 'Tanjay Bus Terminal', 'tanjay', aliases=('Tanjay',)),
            _seed('Bayawan City', 'Negros Oriental', 'Bayawan Bus Terminal', 'bayawan',
                  aliases=('Bayawan',)),
            _seed('Canlaon City', 'Negros Oriental', 'Canlaon Bus Terminal', 'canlaon',
                  aliases=('Canlaon',)),
            _seed('Guihulngan City', 'Negros Oriental', 'Guihulngan Bus Terminal', 'guihulngan',
                  aliases=('Guihulngan',)),
            _seed('Sibulan', 'Negros Oriental', 'Sibulan Bus Stop', 'sibulan',
                  aliases=('Sibulan', 'Sibulan Port'), lat=9.35, lng=123.2833),
            _seed('Amlan', 'Negros Oriental', 'Amlan Bus Stop', 'amlan',
                  aliases=('Amlan',), lat=9.4333, lng=123.2167),
            _seed('San Jose', 'Negros Oriental', 'San Jose Bus Stop', 'san-jose-negros-oriental',
                  aliases=('San Jose Negros Oriental',), lat=9.4167, lng=123.25),
            _seed('Siquijor', 'Siquijor', 'Siquijor Bus Terminal', 'siquijor', aliases=('Siquijor',)),
        ],
    },
    {
        'region': 'Region VIII', 'island': 'Visayas',
        'terminals': [
            _seed('Tacloban City', 'Leyte', 'Tacloban Bus Terminal', 'tacloban',
                  aliases=('Tacloban',)),
            _seed('Ormoc City', 'Leyte', 'Ormoc Bus Terminal', 'ormoc', aliases=('Ormoc',)),
            _seed('Maasin City', 'Southern Leyte', 'Maasin Bus Terminal', 'maasin', aliases=('Maasin',)),
            _seed('Catbalogan City', 'Samar', 'Catbalogan Bus Terminal', 'catbalogan',
                  aliases=('Catbalogan',)),
            _seed('Calbayog City', 'Samar', 'Calbayog Bus Terminal', 'calbayog', aliases=('Calbayog',)),
            _seed('Borongan City', 'Eastern Samar', 'Borongan Bus Terminal', 'borongan',
                  aliases=('Borongan',)),
            _seed('Naval', 'Biliran', 'Naval Bus Terminal', 'naval', aliases=('Naval', 'Biliran')),
            _seed('Baybay City', 'Leyte', 'Baybay Bus Terminal', 'baybay', aliases=('Baybay',)),
            _seed('Hilongos', 'Leyte', 'Hilongos Bus Terminal', 'hilongos', aliases=('Hilongos',)),
            _seed('Palo', 'Leyte', 'Palo Bus Terminal', 'palo', aliases=('Palo',)),
            _seed('Carigara', 'Leyte', 'Carigara Bus Terminal', 'carigara', aliases=('Carigara',)),
        ],
    },
    {
        'region': 'Region IX', 'island': 'Mindanao',
        'terminals': [
            _seed('Zamboanga City', 'Zamboanga del Sur', 'Zamboanga Bus Terminal', 'zamboanga',
                  aliases=('Zamboanga',)),
            _seed('Dipolog City', 'Zamboanga del Norte', 'Dipolog Bus Terminal', 'dipolog',
                  aliases=('Dipolog',)),
            _seed('Dapitan City', 'Zamboanga del Norte', 'Dapitan Bus Terminal', 'dapitan',
                  aliases=('Dapitan',)),
            _seed('Pagadian City', 'Zamboanga del Sur', 'Pagadian Bus Terminal', 'pagadian',
                  aliases=('Pagadian',)),
            _seed('Ipil', 'Zamboanga Sibugay', 'Ipil Bus Terminal', 'ipil', aliases=('Ipil',)),
            _seed('Isabela City', 'Basilan', 'Isabela Bus Terminal', 'isabela-basilan',
                  aliases=('Isabela Basilan',)),
            _seed('Molave', 'Zamboanga del Sur', 'Molave Bus Terminal', 'molave', aliases=('Molave',)),
        ],
    },
    {
        'region': 'Region X', 'island': 'Mindanao',
        'terminals': [
            _seed('Cagayan de Oro', 'Misamis Oriental', 'Cagayan de Oro Bus Terminal', 'cagayan-de-oro',
                  aliases=('Cagayan de Oro', 'CDO', 'Bulua', 'Agora'), hub=True, featured=True),
            _seed('Iligan City', 'Lanao del Norte', 'Iligan Bus Terminal', 'iligan', aliases=('Iligan',)),
            _seed('Gingoog City', 'Misamis Oriental', 'Gingoog Bus Terminal', 'gingoog', aliases=('Gingoog',)),
            _seed('Malaybalay City', 'Bukidnon', 'Malaybalay Bus Terminal', 'malaybalay',
                  aliases=('Malaybalay',)),
            _seed('Valencia City', 'Bukidnon', 'Valencia Bus Terminal', 'valencia', aliases=('Valencia',)),
            _seed('Marawi City', 'Lanao del Sur', 'Marawi Bus Terminal', 'marawi', aliases=('Marawi',)),
            _seed('Ozamiz City', 'Misamis Occidental', 'Ozamiz Bus Terminal', 'ozamiz', aliases=('Ozamiz',)),
            _seed('Oroquieta City', 'Misamis Occidental', 'Oroquieta Bus Terminal', 'oroquieta',
                  aliases=('Oroquieta',)),
            _seed('Tangub City', 'Misamis Occidental', 'Tangub Bus Terminal', 'tangub', aliases=('Tangub',)),
            _seed('Manolo Fortich', 'Bukidnon', 'Manolo Fortich Bus Terminal', 'manolo-fortich',
                  aliases=('Manolo Fortich',)),
        ],
    },
    {
        'region': 'Region XI', 'island': 'Mindanao',
        'terminals': [
            _seed('Davao City', 'Davao del Sur', 'Davao Ecoland Bus Terminal', 'davao-ecoland',
                  aliases=('Davao', 'Ecoland'), hub=True, featured=True),
            _seed('Davao City', 'Davao del Sur', 'Bangkerohan Bus Terminal', 'bangkerohan',
                  aliases=('Bangkerohan',)),
            _seed('Tagum City', 'Davao del Norte', 'Tagum Bus Terminal', 'tagum', aliases=('Tagum',)),
            _seed('Digos City', 'Davao del Sur', 'Digos Bus Terminal', 'digos', aliases=('Digos',)),
            _seed('Panabo City', 'Davao del Norte', 'Panabo Bus Terminal', 'panabo', aliases=('Panabo',)),
            _seed('Mati City', 'Davao Oriental', 'Mati Bus Terminal', 'mati', aliases=('Mati',)),
            _seed('Island Garden City of Samal', 'Davao del Norte', 'Samal Bus Terminal', 'samal',
                  aliases=('Samal',)),
            _seed('Kidapawan City', 'Cotabato', 'Kidapawan Bus Terminal', 'kidapawan',
                  aliases=('Kidapawan',)),
        ],
    },
    {
        'region': 'Region XII', 'island': 'Mindanao',
        'terminals': [
            _seed('General Santos City', 'South Cotabato', 'General Santos Bus Terminal',
                  'general-santos', aliases=('General Santos', 'GenSan')),
            _seed('Koronadal City', 'South Cotabato', 'Koronadal Bus Terminal', 'koronadal',
                  aliases=('Koronadal', 'Marbel')),
            _seed('Cotabato City', 'Maguindanao', 'Cotabato Bus Terminal', 'cotabato',
                  aliases=('Cotabato',)),
            _seed('Tacurong City', 'Sultan Kudarat', 'Tacurong Bus Terminal', 'tacurong',
                  aliases=('Tacurong',)),
            _seed('Isulan', 'Sultan Kudarat', 'Isulan Bus Terminal', 'isulan', aliases=('Isulan',)),
            _seed('Midsayap', 'Cotabato', 'Midsayap Bus Terminal', 'midsayap', aliases=('Midsayap',)),
            _seed('Polomolok', 'South Cotabato', 'Polomolok Bus Terminal', 'polomolok',
                  aliases=('Polomolok',)),
        ],
    },
    {
        'region': 'Region XIII', 'island': 'Mindanao',
        'terminals': [
            _seed('Butuan City', 'Agusan del Norte', 'Butuan Bus Terminal', 'butuan',
                  aliases=('Butuan',)),
            _seed('Surigao City', 'Surigao del Norte', 'Surigao Bus Terminal', 'surigao',
                  aliases=('Surigao',)),
            _seed('Bislig City', 'Surigao del Sur', 'Bislig Bus Terminal', 'bislig', aliases=('Bislig',)),
            _seed('Tandag City', 'Surigao del Sur', 'Tandag Bus Terminal', 'tandag', aliases=('Tandag',)),
            _seed('Bayugan City', 'Agusan del Sur', 'Bayugan Bus Terminal', 'bayugan', aliases=('Bayugan',)),
            _seed('Cabadbaran City', 'Agusan del Norte', 'Cabadbaran Bus Terminal', 'cabadbaran',
                  aliases=('Cabadbaran',)),
            _seed('Prosperidad', 'Agusan del Sur', 'Prosperidad Bus Terminal', 'prosperidad',
                  aliases=('Prosperidad',)),
        ],
    },
    {
        'region': 'BARMM', 'island': 'Mindanao',
        'terminals': [
            _seed('Buluan', 'Maguindanao', 'Maguindanao Bus Terminal', 'buluan',
                  aliases=('Maguindanao',)),
            _seed('Jolo', 'Sulu', 'Jolo Bus Terminal', 'jolo', aliases=('Jolo', 'Sulu')),
            _seed('Bongao', 'Tawi-Tawi', 'Bongao Bus Terminal', 'bongao', aliases=('Bongao', 'Tawi-Tawi')),
            _seed('Lamitan City', 'Basilan', 'Lamitan Bus Terminal', 'lamitan', aliases=('Lamitan',)),
            _seed('Malabang', 'Lanao del Sur', 'Malabang Bus Terminal', 'malabang', aliases=('Malabang',)),
        ],
    },
]


# Everyday kiosk coverage: Negros Occidental and Negros Oriental terminals.
SCOPE_PROVINCES = {'Negros Occidental', 'Negros Oriental'}

TERMINAL_DIRECTORY = []
TERMINAL_BY_SLUG = {}
for _group in REGION_SEEDS:
    for _entry in _group['terminals']:
        if _entry['province'] not in SCOPE_PROVINCES:
            continue
        _entry = dict(_entry)
        # Keep the original province for matching, but island is shared
        _entry['island'] = 'Negros Island'
        _entry['owned'] = False
        TERMINAL_DIRECTORY.append(_entry)
        TERMINAL_BY_SLUG[_entry['slug']] = _entry

_DISPLAY_NAMES = {
    'bacolod-north': 'Bacolod North',
    'bacolod-south': 'Bacolod South',
}
for _entry in TERMINAL_DIRECTORY:
    _entry['name'] = _DISPLAY_NAMES.get(_entry['slug'], _entry['name'])


def _owned_match_keys(master):
    name_key = normalize_name(master.get('name'))
    alias_keys = {
        key for key in (
            normalize_name(alias)
            for alias in (master.get('aliases') or '').split(',')
        ) if key
    }
    keys = {key for key in ({name_key} | alias_keys) if key}
    return name_key, keys


def _merge_owned_terminal(master):
    """Mark the matching directory entry as owned, or add it nationwide."""
    name_key, keys = _owned_match_keys(master)

    candidate = None
    for entry in TERMINAL_DIRECTORY:
        if name_key and name_key in entry['match_keys']:
            candidate = entry
            break

    if candidate is None:
        for entry in TERMINAL_DIRECTORY:
            for key in keys:
                # Skip generic one-word city aliases so Iloilo Jaro/Molo stay distinct.
                if len(key.split()) >= 2 and key in entry['match_keys']:
                    candidate = entry
                    break
            if candidate is not None:
                break

    master_aliases = tuple(
        alias.strip()
        for alias in (master.get('aliases') or '').split(',')
        if alias.strip()
    )

    if candidate is not None:
        candidate['owned'] = True
        candidate['hub'] = True
        candidate['aliases'] = tuple(dict.fromkeys(
            (*candidate['aliases'], master.get('name', ''), *master_aliases)
        ))
        candidate['match_keys'] = tuple(dict.fromkeys(
            (*candidate['match_keys'], *keys)
        ))
        return candidate

    city = master.get('city', '')
    province = master.get('province', '')
    region, island = _PROVINCE_META.get(province, ('Philippines', 'Philippines'))
    label = master.get('name') or city
    preferred = master_aliases[0] if master_aliases else label
    if 'terminal' in preferred.lower() or 'exchange' in preferred.lower():
        terminal = preferred
    elif 'terminal' in label.lower():
        terminal = label
    else:
        terminal = f'{preferred} Terminal'
    entry = _seed(
        city, province, terminal, _slug(label),
        aliases=master_aliases, hub=True, featured=False,
        lat=master.get('lat'), lng=master.get('lng'),
        region=region, island=island,
    )
    entry['owned'] = True
    entry['master_name'] = label
    entry['name'] = label or entry['name']
    entry['match_keys'] = tuple(dict.fromkeys((name_key, *keys)))
    TERMINAL_DIRECTORY.append(entry)
    TERMINAL_BY_SLUG[entry['slug']] = entry
    return entry


for _master in TERMINAL_MASTER_LIST:
    if _master.get('is_owned_terminal'):
        _merge_owned_terminal(_master)

_MATCH_INDEX = {}
for _entry in TERMINAL_DIRECTORY:
    for _key in _entry['match_keys']:
        _MATCH_INDEX.setdefault(_key, _entry)


def get_terminal(slug):
    """Return the terminal directory entry for a slug, or None."""
    if not slug:
        return None
    return TERMINAL_BY_SLUG.get(_slug(slug))


def match_terminal(value):
    """Best-effort match of a free-form terminal name to a directory entry."""
    normalized = normalize_name(value)
    if not normalized:
        return None
    entry = _MATCH_INDEX.get(normalized)
    if entry is not None:
        return entry

    best_entry = None
    best_length = -1
    for candidate in TERMINAL_DIRECTORY:
        for key in candidate['match_keys']:
            if not _token_subset(key, normalized):
                continue
            if len(key) > best_length:
                best_entry = candidate
                best_length = len(key)
    return best_entry


_GROUP_ORDER = ['Negros Island', 'Luzon', 'Visayas', 'Mindanao']
_GROUP_SUBTITLES = {
    'Negros Island': 'Negros Occidental & Oriental',
    'Luzon': 'Vallacar-owned terminals',
    'Visayas': 'Vallacar-owned terminals',
    'Mindanao': 'Vallacar-owned terminals',
}


def terminal_groups():
    """Group the directory by island so the kiosk sidebar reads nationwide."""
    grouped = {}
    for entry in TERMINAL_DIRECTORY:
        island = entry.get('island') or 'Philippines'
        group = grouped.setdefault(island, {
            'region': island,
            'island': _GROUP_SUBTITLES.get(island, 'Vallacar-owned terminals'),
            'terminals': [],
        })
        group['terminals'].append(entry)

    def _order(group):
        island = group['region']
        index = _GROUP_ORDER.index(island) if island in _GROUP_ORDER else len(_GROUP_ORDER)
        return index, island

    groups = sorted(grouped.values(), key=_order)
    for group in groups:
        group['terminals'] = sorted(
            group['terminals'],
            key=lambda entry: (not entry['hub'], entry['name']),
        )
    return groups


def featured_terminals():
    return [entry for entry in TERMINAL_DIRECTORY if entry['featured']]
