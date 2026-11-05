"""FuvarDíj 4.0: 1000 reprodukálható, szintetikus geometriai ellenőrzés.

Ezek nem valós fuvarozói rakodási eredmények és nem bizonyítanak minden esetben optimumot.
"""
import math
import random

import pytest

from packing_optimizer import Tetel, ellenoriz_elhelyezest, optimalizal


def esetek():
    rng = random.Random(20261105)
    for eset_id in range(1000):
        szelesseg = rng.choice((180, 200, 220, 245))
        egysegek = []
        csoportok = rng.randint(1, 3)
        for index in range(csoportok):
            h = rng.choice((40, 50, 60, 70, 80, 90, 100, 120, 140, 160, 180))
            sz = rng.choice((40, 50, 60, 70, 80, 90, 100, 120, 140, 160))
            forgathato = bool(rng.getrandbits(1))
            darab = rng.randint(1, 5)
            egysegek.append(Tetel(index, h, sz, forgathato, darab))
        yield pytest.param(eset_id, szelesseg, egysegek, id=f"synthetic-{eset_id:04d}")


@pytest.mark.parametrize("eset_id,szelesseg,tetelek", list(esetek()))
def test_ezer_szintetikus_elhelyezes(eset_id, szelesseg, tetelek):
    terv = optimalizal(tetelek, 1360, szelesseg, idokorlat_s=0.0)
    assert not ellenoriz_elhelyezest(terv.elhelyezesek, terv.hasznalt_hossz_cm, szelesseg)
    assert len(terv.elhelyezesek) == sum(t.darab for t in tetelek)
    assert terv.also_korlat_cm <= terv.hasznalt_hossz_cm + 1e-7
    terulet = 0
    for t in tetelek:
        csoport = [e for e in terv.elhelyezesek if e.csoport == t.csoport]
        assert len(csoport) == t.darab
        for e in csoport:
            elvart = ((t.szelesseg_cm, t.hossz_cm) if e.forgatott
                       else (t.hossz_cm, t.szelesseg_cm))
            assert (e.hossz_cm, e.szelesseg_cm) == pytest.approx(elvart)
            assert not e.forgatott or t.forgathato
        terulet += t.darab * t.hossz_cm * t.szelesseg_cm
    assert terv.hasznalt_hossz_cm + 1e-7 >= terulet / szelesseg
    assert terv.fedett_terulet_cm2 == pytest.approx(terulet)


@pytest.mark.parametrize("hossz,szelesseg", [
    (0, 80), (-1, 80), (float("nan"), 80),
    (120, 0), (120, float("inf")), (0.001, 80),
])
def test_hibas_meretek_elutasitasa(hossz, szelesseg):
    with pytest.raises(ValueError):
        optimalizal([Tetel(0, hossz, szelesseg, True, 1)], 1360, 245)


def test_nagy_darabszam_nem_futtat_exponencialis_reszhalmazkeresest():
    terv = optimalizal([Tetel(0, 120, 80, True, 100)], 1360, 245, idokorlat_s=0)
    assert len(terv.elhelyezesek) == 100
    assert not ellenoriz_elhelyezest(terv.elhelyezesek, terv.hasznalt_hossz_cm, 245)
