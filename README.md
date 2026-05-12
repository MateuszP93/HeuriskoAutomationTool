# Heurisko Automation Tool

Konsolowy framework do sterowania aplikacją Heurisko bez natywnego API.

## Instalacja

```powershell
python -m pip install -r requirements.txt
```

## Szybki Test Konfiguracji

```powershell
python main.py inspect --no-connect
```

## Live Shell

Uruchom Heurisko, upewnij się, że tytuł okna pasuje do `configs/windows.yaml`, a potem:

```powershell
python main.py shell
```

W shellu dostępny jest obiekt `heurisko`:

```python
heurisko.acc.set_irradiance(20)
```

Można też otworzyć okno i sterować nim ręcznie:

```python
dialog = heurisko.acc.open_set_irradiance()
dialog.click("value_field")
dialog.write("20")
dialog.click("ok_button")
```

## Workflow

Uruchomienie pojedynczego workflow:

```powershell
python main.py run acc_set_irradiance --param irradiance=20 --run-id acc_001
```

Uruchomienie kolejki:

```powershell
python main.py run-queue data/input/queue.yaml
```

## Status Zakończenia Testu

Domyślny plik statusu:

```text
data/runtime/heurisko_status.txt
```

Oczekiwany wpis kończący test:

```text
$$DONE$$ run_id=acc_001 status=OK
```

Przy ręcznym `heurisko.acc.set_irradiance(20)` framework nie czeka na status. Przy kolejce i standardowym workflow krok `wait_done` będzie czekał na wpis z aktualnym `run_id`.

## Najczęściej Edytowane Pliki

- `configs/windows.yaml` - regexy tytułów okien, rozmiar głównego okna, lokatory w popupach.
- `configs/locators.yaml` - kliknięcia w menu głównym.
- `configs/workflows/*.yaml` - procedury testowe.
- `data/input/queue.yaml` - przykładowa kolejka testów.
