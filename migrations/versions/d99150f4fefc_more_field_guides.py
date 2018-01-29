"""more field guides

Revision ID: d99150f4fefc
Revises: b25352d6508f
Create Date: 2018-01-29 14:13:02.121671

"""

# revision identifiers, used by Alembic.
revision = 'd99150f4fefc'
down_revision = 'b25352d6508f'
branch_labels = None
depends_on = None

import sqlalchemy as sa
from alembic import op

VPREFIX = 'https://cdstar.shh.mpg.de/bitstreams/'
PDF_URLS = {
    "tebulure": "EAEA0-433D-37B3-48AA-0/tebulure.pdf",
    "spa": "EAEA0-4154-2E15-23C0-0/spa.pdf",
    "lwn-h": "EAEA0-72EC-D2B8-23D9-0/lwn-h.pdf",
    "huc": "EAEA0-95F9-E33D-4659-0/huc.pdf",
    "lue": "EAEA0-5919-3E54-966F-0/lue.pdf",
    "bankantey": "EAEA0-85DB-B1AD-79AA-0/bankantey.pdf",
    "najamba": "EAEA0-2DE8-13B8-65AE-0/najamba.pdf",
    "kon": "EAEA0-E43E-7A08-6CE7-0/kon.pdf",
    "nhr": "EAEA0-D387-F80E-FB79-0/nhr.pdf",
    "bds": "EAEA0-AEE3-3D67-577D-0/bds.pdf",
    "kam": "EAEA0-9D5B-D33F-773C-0/kam.pdf",
    "dal": "EAEA0-4347-205D-F91E-0/dal.pdf",
    "sad": "EAEA0-D94A-1582-3D61-0/sad.pdf",
    "bej": "EAEA0-CAAD-2E4C-32B1-0/bej.pdf",
    "umb": "EAEA0-CDC5-C907-3E6A-0/umb.pdf",
    "arb": "EAEA0-2DB1-A4AE-9B6D-0/arb.pdf",
    "vmw": "EAEA0-989B-97E9-D1BD-0/vmw.pdf",
    "her": "EAEA0-0313-5E6A-D797-0/her.pdf",
    "kin": "EAEA0-7018-C80A-35BF-0/kin.pdf",
    "nanga": "EAEA0-D602-35E4-A289-0/nanga.pdf",
    "bunoge": "EAEA0-2F7E-E4EE-A623-0/bunoge.pdf",
    "guz": "EAEA0-C670-D004-4749-0/guz.pdf",
    "ktz": "EAEA0-3822-CFC3-795B-0/ktz.pdf",
    "penange": "EAEA0-653F-6B51-AC87-0/penange.pdf",
    "yandadom": "EAEA0-E8FD-2D69-E810-0/yandadom.pdf",
    "irk": "EAEA0-8D14-C580-BAB8-0/irk.pdf",
    "fwe": "EAEA0-5F56-8FC1-2052-0/fwe.pdf",
    "doguldom": "EAEA0-C01A-2DC4-053A-0/doguldom.pdf",
    "gwj": "EAEA0-574C-A007-40F3-0/gwj.pdf",
    "kua": "EAEA0-74B1-ACBA-3AC5-0/kua.pdf",
    "hio-h": "EAEA0-892C-8C93-643A-0/hio-h.pdf",
    "protokalaharikhoe": "EAEA0-AD10-D73F-FA7B-0/protokalaharikhoe.pdf",
    "nde": "EAEA0-72A0-7412-82B5-0/nde.pdf",
    "shg-de": "EAEA0-F14D-7887-6A7C-0/shg-de.pdf",
    "fra": "EAEA0-EFA0-2572-3F14-0/fra.pdf",
    "protohighlandeastcushitic": "EAEA0-194B-6163-2115-0/protohighlandeastcushitic.pdf",
    "knw": "EAEA0-7848-CB90-0724-0/knw.pdf",
    "tsc": "EAEA0-44E5-5DA7-93A6-0/tsc.pdf",
    "nmn-w": "EAEA0-1328-D90C-9BA8-0/nmn-w.pdf",
    "jamsaymondoro": "EAEA0-422B-4902-EE9E-0/jamsaymondoro.pdf",
    "lun": "EAEA0-7D43-79C6-20D5-0/lun.pdf",
    "sbs": "EAEA0-F58F-0513-EEEB-0/sbs.pdf",
    "ampari": "EAEA0-CC3B-23C7-FAC2-0/ampari.pdf",
    "deu": "EAEA0-E9F6-9049-630A-0/deu.pdf",
    "kde": "EAEA0-F872-EC1B-6878-0/kde.pdf",
    "byn": "EAEA0-0E3F-73D2-CBD4-0/byn.pdf",
    "dsh": "EAEA0-B1C1-C907-F862-0/dsh.pdf",
    "swa": "EAEA0-CD1B-E617-612C-0/swa.pdf",
    "xuu-a": "EAEA0-AA4A-0137-7429-0/xuu-a.pdf",
    "lin": "EAEA0-483F-5EDE-C55F-0/lin.pdf",
    "ewo": "EAEA0-F327-CB1A-8AB9-0/ewo.pdf",
    "xeg": "EAEA0-9D23-FB02-E9F8-0/xeg.pdf",
    "protosouthcushitic": "EAEA0-C5BA-464C-0D75-0/protosouthcushitic.pdf",
    "kuvale": "EAEA0-F1B7-0369-FAE0-0/kuvale.pdf",
    "mombo": "EAEA0-EAC5-CF4C-A52F-0/mombo.pdf",
    "tommoso": "EAEA0-2899-F861-3919-0/tommoso.pdf",
    "rng": "EAEA0-C857-669D-13FF-0/rng.pdf",
    "lwn-a": "EAEA0-D849-326B-0E73-0/lwn-a.pdf",
    "nya": "EAEA0-E636-E504-966D-0/nya.pdf",
    "toh": "EAEA0-A0FF-A31E-A77D-0/toh.pdf",
    "tum": "EAEA0-F60E-C9CA-FAFA-0/tum.pdf",
    "nyy": "EAEA0-2A3B-7777-159A-0/nyy.pdf",
    "amh": "EAEA0-8608-2136-0B9D-0/amh.pdf",
    "hts": "EAEA0-2F16-9D77-EF13-0/hts.pdf",
    "seh": "EAEA0-AC46-A946-C7E2-0/seh.pdf",
    "niy": "EAEA0-B4F3-2680-333D-0/niy.pdf",
    "naq-a": "EAEA0-DFB3-EFDF-F1B5-0/naq-a.pdf",
    "tso": "EAEA0-331D-D72D-C497-0/tso.pdf",
    "naq": "EAEA0-ECBA-79A0-9D8A-0/naq.pdf",
    "xuu-b": "EAEA0-2A28-A667-C604-0/xuu-b.pdf",
    "lua": "EAEA0-9C4D-DF18-D83E-0/lua.pdf",
    "sna": "EAEA0-3E30-FBA6-34BC-0/sna.pdf",
    "zne": "EAEA0-4A69-53A4-64C3-0/zne.pdf",
    "kwn": "EAEA0-F7E3-C2E4-2945-0/kwn.pdf",
    "toi": "EAEA0-3963-8E8C-B0EA-0/toi.pdf",
    "mdj": "EAEA0-DBA5-28EB-138A-0/mdj.pdf",
    "nmn-h": "EAEA0-22C4-A7B9-45A7-0/nmn-h.pdf",
    "yey": "EAEA0-72EF-245A-B513-0/yey.pdf",
    "xho": "EAEA0-23A8-3472-0EC3-0/xho.pdf",
    "ndc": "EAEA0-60C7-8979-42AB-0/ndc.pdf",
    "yao": "EAEA0-3180-FA03-4E2B-0/yao.pdf",
    "nmn-e": "EAEA0-74CB-814F-F332-0/nmn-e.pdf",
    "kqz": "EAEA0-52DB-4C5D-43BF-0/kqz.pdf",
    "tomokandiangassagou": "EAEA0-DA95-D1BB-7B90-0/tomokandiangassagou.pdf",
    "kck": "EAEA0-088B-65E1-E197-0/kck.pdf",
    "togokan": "EAEA0-A93A-9B32-AF2E-0/togokan.pdf",
    "kwz": "EAEA0-ED80-B7B6-1486-0/kwz.pdf",
    "nse": "EAEA0-9506-FE23-146B-0/nse.pdf",
    "kel": "EAEA0-11F7-6912-A4DF-0/kel.pdf",
    "eng": "EAEA0-900F-8115-9E07-0/eng.pdf",
    "fan": "EAEA0-BB4B-E1C7-0264-0/fan.pdf",
    "lub": "EAEA0-613A-808A-2BB8-0/lub.pdf",
    "nyk": "EAEA0-D1A6-6743-50DD-0/nyk.pdf",
    "loz": "EAEA0-8647-4C32-94DC-0/loz.pdf",
    "kik": "EAEA0-FB98-5BE3-3359-0/kik.pdf",
    "cce": "EAEA0-43AE-1E30-D628-0/cce.pdf",
    "afr": "EAEA0-7650-FF3B-27D1-0/afr.pdf",
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
