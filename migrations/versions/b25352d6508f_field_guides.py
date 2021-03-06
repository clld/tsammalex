"""field guides

Revision ID: b25352d6508f
Revises: 3a11c87ddfd7
Create Date: 2018-01-29 10:21:24.851812

"""

# revision identifiers, used by Alembic.
revision = 'b25352d6508f'
down_revision = '3a11c87ddfd7'
branch_labels = None
depends_on = None

import json

import sqlalchemy as sa
from alembic import op

VPREFIX = 'https://cdstar.shh.mpg.de/bitstreams/'
PDF_URLS = {
    "protoagaw": "EAEA0-A2F0-0C49-9FFB-0/protoagaw.pdf",
    "ssw": "EAEA0-E468-900E-98BF-0/ssw.pdf",
    "torotegu": "EAEA0-4261-A275-B6F4-0/torotegu.pdf",
    "lam": "EAEA0-1120-C5AF-7AC6-0/lam.pdf",
    "mas": "EAEA0-379A-23C6-ACF7-0/mas.pdf",
    "tsn": "EAEA0-3B23-A54D-BC76-0/tsn.pdf",
    "naq-n": "EAEA0-2901-D747-B536-0/naq-n.pdf",
    "bas": "EAEA0-3450-0205-FEEC-0/bas.pdf",
    "nyn": "EAEA0-DD93-0E0B-30D5-0/nyn.pdf",
    "naq-hm": "EAEA0-54EC-C0B9-3724-0/naq-hm.pdf",
    "pergetegu": "EAEA0-4CF6-E175-37F6-0/pergetegu.pdf",
    "mcp": "EAEA0-C2D1-2815-5A1E-0/mcp.pdf",
    "ndo": "EAEA0-7EB5-FE37-8FA0-0/ndo.pdf",
    "kmb": "EAEA0-D880-14B6-881D-0/kmb.pdf",
    "run": "EAEA0-FA58-1E65-A8EB-0/run.pdf",
    "mhw": "EAEA0-4919-20C0-B18A-0/mhw.pdf",
    "swh": "EAEA0-C374-6ADB-1465-0/swh.pdf",
    "yornoso": "EAEA0-8729-3D8C-A865-0/yornoso.pdf",
    "tomokan": "EAEA0-7D40-294F-E6C6-0/tomokan.pdf",
    "hay": "EAEA0-59A8-1F6F-D9FC-0/hay.pdf",
    "mer": "EAEA0-7CB5-D24B-ED0F-0/mer.pdf",
    "lug": "EAEA0-73F7-C8A1-8506-0/lug.pdf",
    "lch": "EAEA0-FB09-BA0C-13ED-0/lch.pdf",
    "nih": "EAEA0-CDA5-250C-E821-0/nih.pdf",
    "cjk": "EAEA0-C6C1-F02B-FA13-0/cjk.pdf",
    "sot": "EAEA0-9831-5D27-F5B6-0/sot.pdf",
    "donnoso": "EAEA0-37A4-B142-8D49-0/donnoso.pdf",
    "nso": "EAEA0-B8FA-B439-72CC-0/nso.pdf",
    "suk": "EAEA0-1152-AAD7-9A1B-0/suk.pdf",
    "luo": "EAEA0-0CCF-D3B7-B28A-0/luo.pdf",
    "naq-d": "EAEA0-C58A-429B-D3F1-0/naq-d.pdf",
    "asa": "EAEA0-D118-516E-58B0-0/asa.pdf",
    "laj": "EAEA0-871D-BAB3-1EFF-0/laj.pdf",
    "ngh-w": "EAEA0-CE9A-B4D7-D4F9-0/ngh-w.pdf",
    "hio-g": "EAEA0-33DB-AEA4-5A0B-0/hio-g.pdf",
    "gourou": "EAEA0-40B7-E90D-8858-0/gourou.pdf",
    "gmv": "EAEA0-8A1C-294C-5A14-0/gmv.pdf",
    "ven": "EAEA0-3EC4-12BB-FDE7-0/ven.pdf",
    "mgd": "EAEA0-F5CC-ABCC-4BF3-0/mgd.pdf",
    "pbr": "EAEA0-21DC-F14A-2584-0/pbr.pdf",
    "nmn-a": "EAEA0-E6EE-A14D-63D8-0/nmn-a.pdf",
    "som": "EAEA0-601D-56F8-669B-0/som.pdf",
    "nmn-t": "EAEA0-9615-34DB-1E75-0/nmn-t.pdf",
    "shg-da": "EAEA0-E665-DCED-13C5-0/shg-da.pdf",
    "nyf": "EAEA0-704C-E839-F1DA-0/nyf.pdf",
    "tiranige": "EAEA0-511B-6D69-0363-0/tiranige.pdf",
    "txk": "EAEA0-6172-B119-DBDF-0/txk.pdf",
    "xuu-k": "EAEA0-825F-7AAB-144C-0/xuu-k.pdf",
    "ngh-e": "EAEA0-DD9D-52EE-268F-0/ngh-e.pdf",
    "diu": "EAEA0-0FC1-B949-3963-0/diu.pdf",
    "ikx": "EAEA0-2F50-95D6-8C2C-0/ikx.pdf",
    "por": "EAEA0-8921-3153-2ABF-0/por.pdf",
    "xkv": "EAEA0-5AEB-97AE-5056-0/xkv.pdf",
    "bem": "EAEA0-3119-428B-997A-0/bem.pdf",
    "sid": "EAEA0-18A2-95E7-9C21-0/sid.pdf",
    "jamsay": "EAEA0-FCE3-0D26-0E6D-0/jamsay.pdf",
    "nba": "EAEA0-E6AB-6888-5383-0/nba.pdf",
    "ibiso": "EAEA0-B851-78F7-C354-0/ibiso.pdf",
    "mgw": "EAEA0-0BED-8103-8E3F-0/mgw.pdf",
    "mfc": "EAEA0-B773-17C1-6403-0/mfc.pdf",
    "gwd-gol": "EAEA0-33DC-460F-9B9E-0/gwd-gol.pdf",
    "lea": "EAEA0-0A2F-3E8E-2F67-0/lea.pdf",
    "nbl": "EAEA0-1A21-F86A-A8C8-0/nbl.pdf",
    "zul": "EAEA0-B09C-C55E-FB5A-0/zul.pdf",
    "gku": "EAEA0-E15A-7F1E-A698-0/gku.pdf",
    "puu": "EAEA0-94A5-3894-EB99-0/puu.pdf",
    "protosemitic": "EAEA0-C38E-17BA-C684-0/protosemitic.pdf",
    "bentey": "EAEA0-057C-07B6-3A78-0/bentey.pdf",
    "xam": "EAEA0-95CD-A5C9-93DC-0/xam.pdf",
    "mye-or": "EAEA0-2042-6BD3-1E7C-0/mye-or.pdf"
}


def upgrade():
    urlmap = {}

    for k, v in PDF_URLS.items():
        urlmap[k] = VPREFIX + v

    for k, v in urlmap.items():
        url = '{"pdf_url": "' + v + '"}'
        query = sa.text(
            'UPDATE language SET jsondata = :jsondata WHERE id = :id'
        ).bindparams(jsondata=url, id=k)

        op.execute(query)


def downgrade():
    pass
