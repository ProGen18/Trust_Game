import hashlib
import hmac
import sys
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest

import config
from bilendi.views import EntryView
from bilendi.services import compute_total_gain, validate_and_start, complete_participant, abandon_stale_registrations


# =============================================================================
# Fixture : injecte un faux bilendi.models dans sys.modules pour éviter
# que les imports locaux (inside-function) n'essaient de charger Django ORM
# =============================================================================

@pytest.fixture()
def fake_reg():
    """Retourne un mock de BilendiRegistration et l'injecte dans sys.modules."""
    MockReg = MagicMock()
    mock_module = MagicMock()
    mock_module.BilendiRegistration = MockReg
    with patch.dict(sys.modules, {"bilendi.models": mock_module}):
        yield MockReg


# =============================================================================
# Helpers
# =============================================================================

def make_token(bilendi_id: str, secret: str = None) -> str:
    """Génère un token HMAC-SHA256 valide pour un bilendi_id donné."""
    secret = secret or config.SECRET_KEY
    sig = hmac.new(secret.encode(), bilendi_id.encode(), hashlib.sha256).hexdigest()
    return f"{bilendi_id}:{sig}"


def mock_participant(bilendi_id=None, show_up=2.5, risk=1.0, tg=3.0, tg_skipped=False):
    """Crée un faux participant oTree avec les vars nécessaires."""
    p = MagicMock()
    p.vars = {
        "bilendi_id": bilendi_id,
        "total_risk_aversion": risk,
        "tg_gain": tg,
        "trust_game_skipped": tg_skipped,
    }
    return p


# =============================================================================
# Tests — _verify_token
# =============================================================================

class TestVerifyToken:
    def setup_method(self):
        self.view = EntryView()

    def test_token_valide_retourne_bilendi_id(self):
        token = make_token("abc-123")
        assert self.view._verify_token(token) == "abc-123"

    def test_token_valide_avec_id_complexe(self):
        bilendi_id = "user:sub:detail"
        token = make_token(bilendi_id)
        # rpartition sur ":" → seule la dernière partie est la signature
        assert self.view._verify_token(token) == bilendi_id

    def test_token_signature_incorrecte(self):
        token = "abc-123:signaturefausse"
        assert self.view._verify_token(token) is None

    def test_token_vide(self):
        assert self.view._verify_token("") is None

    def test_token_sans_separateur(self):
        assert self.view._verify_token("pasdedeux-points") is None

    def test_token_none(self):
        assert self.view._verify_token(None) is None

    def test_token_mauvais_secret(self):
        token = make_token("abc-123", secret="mauvais-secret")
        assert self.view._verify_token(token) is None

    def test_token_tronque(self):
        token = make_token("abc-123")
        assert self.view._verify_token(token[:-4]) is None


# =============================================================================
# Tests — EntryView GET
# =============================================================================

class TestEntryViewGet:
    def _make_request(self):
        req = MagicMock()
        req.method = "GET"
        return req

    @patch("bilendi.views.config")
    @patch("bilendi.views.render")
    def test_get_bilendi_active_affiche_formulaire(self, mock_render, mock_config):
        mock_config.BILENDI_ENABLED = True
        view = EntryView()
        req = self._make_request()
        view.get(req)
        mock_render.assert_called_once_with(req, "bilendi/entry.html")

    @patch("bilendi.views.config")
    def test_get_bilendi_desactive_leve_404(self, mock_config):
        from django.http import Http404
        mock_config.BILENDI_ENABLED = False
        view = EntryView()
        req = self._make_request()
        with pytest.raises(Http404):
            view.get(req)


# =============================================================================
# Tests — EntryView POST
# =============================================================================

class TestEntryViewPost:
    def _make_request(self, token="", ip="127.0.0.1"):
        req = MagicMock()
        req.method = "POST"
        req.POST = {"token": token}
        req.META = {"REMOTE_ADDR": ip}
        req.session = {}
        return req

    @patch("bilendi.views.config")
    def test_post_bilendi_desactive_leve_404(self, mock_config):
        from django.http import Http404
        mock_config.BILENDI_ENABLED = False
        view = EntryView()
        req = self._make_request(token=make_token("id-1"))
        with pytest.raises(Http404):
            view.post(req)

    @patch("bilendi.views.config")
    @patch("bilendi.views.render")
    def test_post_token_invalide_retourne_400(self, mock_render, mock_config):
        mock_config.BILENDI_ENABLED = True
        mock_config.SECRET_KEY = config.SECRET_KEY
        view = EntryView()
        req = self._make_request(token="faux:token")
        view.post(req)
        mock_render.assert_called_once()
        assert mock_render.call_args.kwargs["status"] == 400

    @patch("bilendi.views.config")
    @patch("bilendi.views.render")
    def test_post_token_vide_retourne_400(self, mock_render, mock_config):
        mock_config.BILENDI_ENABLED = True
        mock_config.SECRET_KEY = config.SECRET_KEY
        view = EntryView()
        req = self._make_request(token="")
        view.post(req)
        mock_render.assert_called_once()
        assert mock_render.call_args.kwargs["status"] == 400

    @patch("bilendi.views.config")
    @patch("bilendi.views.render")
    @patch("bilendi.views.validate_and_start", return_value=False)
    def test_post_participant_deja_commence_retourne_400(
        self, mock_validate, mock_render, mock_config
    ):
        mock_config.BILENDI_ENABLED = True
        mock_config.SECRET_KEY = config.SECRET_KEY

        fake_session = MagicMock()
        fake_session.code = "sess01"

        view = EntryView()
        view._get_bilendi_session = MagicMock(return_value=fake_session)

        req = self._make_request(token=make_token("id-deja-utilise"))
        view.post(req)
        mock_render.assert_called_once()
        assert mock_render.call_args.kwargs["status"] == 400

    @patch("bilendi.views.config")
    @patch("bilendi.views.render")
    def test_post_session_introuvable_retourne_503(self, mock_render, mock_config):
        mock_config.BILENDI_ENABLED = True
        mock_config.SECRET_KEY = config.SECRET_KEY

        view = EntryView()
        view._get_bilendi_session = MagicMock(return_value=None)

        req = self._make_request(token=make_token("id-ok"))
        view.post(req)
        mock_render.assert_called_once()
        assert mock_render.call_args.kwargs["status"] == 503

    @patch("bilendi.views.config")
    @patch("bilendi.views.redirect")
    @patch("bilendi.views.validate_and_start", return_value=True)
    def test_post_valide_stocke_session_et_redirige(
        self, mock_validate, mock_redirect, mock_config
    ):
        mock_config.BILENDI_ENABLED = True
        mock_config.SECRET_KEY = config.SECRET_KEY

        fake_session = MagicMock()
        fake_session.code = "sess42"

        view = EntryView()
        view._get_bilendi_session = MagicMock(return_value=fake_session)

        req = self._make_request(token=make_token("id-nouveau"))
        view.post(req)

        assert req.session["bilendi_id"] == "id-nouveau"
        assert req.session["bilendi_session_code"] == "sess42"
        mock_redirect.assert_called_once_with("/join/sess42")


# =============================================================================
# Tests — services.compute_total_gain
# =============================================================================

class TestComputeTotalGain:
    @patch("bilendi.services.config")
    def test_gain_standard(self, mock_config):
        mock_config.SHOW_UP_FEE = 2.5
        p = mock_participant(risk=1.0, tg=3.0)
        assert compute_total_gain(p) == 6.5

    @patch("bilendi.services.config")
    def test_gain_zero_partout(self, mock_config):
        mock_config.SHOW_UP_FEE = 0.0
        p = mock_participant(risk=0.0, tg=0.0)
        assert compute_total_gain(p) == 0.0

    @patch("bilendi.services.config")
    def test_gain_arrondi_deux_decimales(self, mock_config):
        mock_config.SHOW_UP_FEE = 2.5
        p = mock_participant(risk=0.123456, tg=1.0)
        result = compute_total_gain(p)
        assert result == round(2.5 + 0.123456 + 1.0, 2)

    @patch("bilendi.services.config")
    def test_gain_vars_absents_valent_zero(self, mock_config):
        mock_config.SHOW_UP_FEE = 2.5
        p = MagicMock()
        p.vars = {}
        result = compute_total_gain(p)
        assert result == 2.5


# =============================================================================
# Tests — services.validate_and_start
# =============================================================================

class TestValidateAndStart:
    @patch("bilendi.services.timezone")
    @patch("bilendi.services.transaction")
    def test_passage_imported_vers_started(self, mock_tx, mock_tz, fake_reg):
        mock_tx.atomic.return_value.__enter__ = MagicMock(return_value=None)
        mock_tx.atomic.return_value.__exit__ = MagicMock(return_value=False)
        mock_tz.now.return_value = datetime(2026, 1, 1)
        qs = MagicMock()
        qs.select_for_update.return_value = qs
        qs.filter.return_value = qs
        qs.update.return_value = 1
        fake_reg.objects = qs

        result = validate_and_start("id-ok", "part-abc")
        assert result is True

    @patch("bilendi.services.timezone")
    @patch("bilendi.services.transaction")
    def test_participant_deja_started_retourne_false(self, mock_tx, mock_tz, fake_reg):
        mock_tx.atomic.return_value.__enter__ = MagicMock(return_value=None)
        mock_tx.atomic.return_value.__exit__ = MagicMock(return_value=False)
        mock_tz.now.return_value = datetime(2026, 1, 1)
        qs = MagicMock()
        qs.select_for_update.return_value = qs
        qs.filter.return_value = qs
        qs.update.return_value = 0
        fake_reg.objects = qs

        result = validate_and_start("id-deja-pris", "part-xyz")
        assert result is False


# =============================================================================
# Tests — services.complete_participant
# =============================================================================

class TestCompleteParticipant:
    @patch("bilendi.services.config")
    @patch("bilendi.services.timezone")
    def test_participant_complete_mis_a_jour(self, mock_tz, mock_config, fake_reg):
        mock_config.SHOW_UP_FEE = 2.5
        mock_tz.now.return_value = datetime(2026, 1, 1)

        qs = MagicMock()
        qs.filter.return_value = qs
        qs.update.return_value = 1
        fake_reg.objects = qs

        p = mock_participant(bilendi_id="id-fin", risk=1.0, tg=2.0)
        complete_participant(p)

        qs.filter.assert_called_once_with(bilendi_id="id-fin", status="started")
        update_kwargs = qs.update.call_args[1]
        assert update_kwargs["status"] == "completed"
        assert update_kwargs["computed_gain"] == 5.5

    def test_participant_sans_bilendi_id_ne_fait_rien(self):
        p = MagicMock()
        p.vars = {}
        complete_participant(p)

    @patch("bilendi.services.config")
    @patch("bilendi.services.timezone")
    def test_tg_skipped_enregistre(self, mock_tz, mock_config, fake_reg):
        mock_config.SHOW_UP_FEE = 2.5
        mock_tz.now.return_value = datetime(2026, 1, 1)

        qs = MagicMock()
        qs.filter.return_value = qs
        qs.update.return_value = 1
        fake_reg.objects = qs

        p = mock_participant(bilendi_id="id-skip", tg_skipped=True)
        complete_participant(p)

        update_kwargs = qs.update.call_args[1]
        assert update_kwargs["trust_game_skipped"] is True


# =============================================================================
# Tests — services.abandon_stale_registrations
# =============================================================================

class TestAbandonStale:
    @patch("bilendi.services.timezone")
    def test_marque_started_inactifs_comme_abandonnes(self, mock_tz, fake_reg):
        now = datetime(2026, 1, 1, 12, 0, 0)
        mock_tz.now.return_value = now
        mock_tz.timedelta = timedelta

        qs = MagicMock()
        qs.filter.return_value = qs
        qs.update.return_value = 3
        fake_reg.objects = qs

        count = abandon_stale_registrations(7200)
        assert count == 3
        qs.filter.assert_called_once_with(
            status="started",
            last_activity_at__lt=now - timedelta(seconds=7200),
        )
        qs.update.assert_called_once_with(status="abandoned")

    @patch("bilendi.services.timezone")
    def test_aucun_inactif_retourne_zero(self, mock_tz, fake_reg):
        mock_tz.now.return_value = datetime(2026, 1, 1)
        mock_tz.timedelta = timedelta

        qs = MagicMock()
        qs.filter.return_value = qs
        qs.update.return_value = 0
        fake_reg.objects = qs

        count = abandon_stale_registrations(3600)
        assert count == 0
