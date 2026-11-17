"""Tests unitaires des règles de prix — POINT DE DÉPART (Atelier 1).

Complétez ce fichier : objectif >= 90 % de couverture sur minishop/pricing.py.
"""

from decimal import Decimal

import pytest

from minishop.pricing import line_total, money, quote

x=1

pytestmark = pytest.mark.unit


def test_money_arrondi_commercial():
    """0.125 s'arrondit à 0.13 (ROUND_HALF_UP), pas 0.12."""
    assert money("0.125") == Decimal("0.13")

# def test_money_mode_bug_rounding(monkeypatch):
#     # Active le mode de démonstration du bug :
#     # quantize() utilise alors ROUND_HALF_EVEN par défaut.
#     monkeypatch.setenv("MINISHOP_BUG", "rounding")
#     assert money("0.125") == Decimal("0.12")

def test_line_total_sans_remise():
    assert line_total(Decimal("12.50"), 2) == Decimal("25.00")


def test_quote_panier_vide():
    """Un panier vide coûte 0 € : pas de frais de livraison."""
    q = quote([])
    assert q.total == Decimal("0.00")
    assert q.shipping == Decimal("0.00")

@pytest.mark.parametrize("qty", [0, -1, 100, "2", True])
def test_quantite_invalide(qty):
    with pytest.raises(ValueError):
        line_total(Decimal("10"), qty)

def test_line_total_remise_volume():
    """10 mugs à 12,50 € : remise de 5 % sur le total."""
    assert line_total(Decimal("12.50"), 10) == Decimal("118.75")  # 125 - 6,25    

def test_line_total_remise_volume_9():
    """9 mugs à 12,50 € : pas de remise."""
    assert line_total(Decimal("12.50"), 9) == Decimal("112.50")  # pas de remise   

@pytest.mark.parametrize("coupon", ["WELCOME10", "welcome10", " Welcome10 "])
def test_coupon_welcome10_casse(coupon):
    q = quote([{"product_id": "mug", "qty": 2}], coupon=coupon)

    assert q.discount == Decimal("2.50")
    assert q.total == Decimal("27.40")

@pytest.mark.parametrize("coupon", ["FIXED5", "fixed5", " Fixed5 "])
def test_coupon_fixed5_casse(coupon):
    q = quote([{"product_id": "tshirt", "qty": 2}], coupon=coupon)

    assert q.discount == Decimal("5.00")
    assert q.total == Decimal("39.70")


@pytest.mark.parametrize("coupon", ["FREESHIP", "freeship", " Freeship "])
def test_coupon_freeship_casse(coupon):
    q = quote([{"product_id": "hoodie", "qty": 1}], coupon=coupon)

    assert q.discount == Decimal("0.00")
    assert q.shipping == Decimal("0.00")
    assert q.total == Decimal("44.00")

@pytest.mark.parametrize("coupon", ["STUDENT15", "student15", " Student15 "])
def test_coupon_student15_casse(coupon):
    q = quote([{"product_id": "hoodie", "qty": 1}], coupon=coupon)

    assert q.discount == Decimal("6.60")
    assert q.total == Decimal("42.30")

def test_coupon_student15_non_cumulable():
    """STUDENT15 n'est pas cumulable avec la remise volume."""
    q = quote([{"product_id": "mug", "qty": 10}], coupon="STUDENT15")

    assert q.discount == Decimal("0")
    assert q.total == Decimal("118.75")

def test_coupon_inconnu():
    with pytest.raises(ValueError):
        quote([{"product_id": "mug", "qty": 1}], coupon="UNKNOWN")

def test_coupon_null():
    """Coupon vide ou None : pas de remise."""
    q1 = quote([{"product_id": "mug", "qty": 2}], coupon="")
    q2 = quote([{"product_id": "mug", "qty": 2}], coupon=None)

    assert q1.discount == Decimal("0.00")
    assert q2.discount == Decimal("0.00")

def test_quote_as_dict_panier_vide():
    q = quote([])

    assert q.as_dict() == {
        "lines": [],
        "subtotal": "0.00",
        "discount": "0.00",
        "shipping": "0.00",
        "total": "0.00",
        "coupon": None,
    }

def test_livraison_offerte_apres_remise():
    """Livraison offerte à partir de 50 € APRÈS remise."""
    q = quote([{"product_id": "hoodie", "qty": 2}], coupon="WELCOME10")
    assert q.subtotal == Decimal("88.00")
    assert q.discount == Decimal("8.80")
    assert q.shipping == Decimal("0.00")  # livraison offerte
    assert q.total == Decimal("79.20")

def test_produit_inconnu():
    """Produit inconnu -> KeyError."""
    with pytest.raises(KeyError):
        quote([{"product_id": "unknown", "qty": 1}])

# TODO Atelier 1 :
#  - remise volume à partir de 10 unités (et pas à 9 !) ✅
#  - quantités invalides (0, 100, -1, "2", True) -> ValueError   (astuce : @pytest.mark.parametrize) ✅
#  - coupons WELCOME10 / FIXED5 / FREESHIP (seuils inclus/exclus), coupon inconnu, casse ✅
#  - livraison offerte à partir de 50 € APRÈS remise ✅
#  - produit inconnu -> KeyError✅
