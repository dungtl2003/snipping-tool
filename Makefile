ROOT_DIR = $(shell pwd)
ENV_DIR = $(ROOT_DIR)/env
PYTHON = $(ENV_DIR)/bin/activate

# Check if the virtual environment exists, if not create it
VENV_CHECK = $(shell if [ ! -d "$(ENV_DIR)" ]; then echo "not_exists"; fi)

# Target to generate the script
gen_script_linux:
	@echo "Generating script"
	$(ROOT_DIR)/scripts/create_env.sh
	. $(PYTHON) && pip install -r requirements.txt && pyinstaller --onefile --add-data "assets/icons:assets/icons" --add-data "assets/animations:assets/animations" --add-data "credentials.json:." --name Becap --windowed main.py

clean_linux: uninstall_linux
	echo "Cleaning up"
	rm -rf dist
	rm -rf build
	rm -rf __pycache__

build_app_linux:
	echo "Creating nessessary directories"
	mkdir -p $(HOME)/.local/share/icons/hicolor/256x256/apps
	mkdir -p $(HOME)/.local/share/icons/hicolor/128x128/apps
	mkdir -p $(HOME)/.local/share/icons/hicolor/64x64/apps
	mkdir -p $(HOME)/.local/share/icons/hicolor/32x32/apps
	mkdir -p $(HOME)/.local/share/icons/hicolor/16x16/apps
	mkdir -p $(HOME)/.local/share/applications

	echo "Copying icons and desktop file"
	cp assets/256x256/scissor.png $(HOME)/.local/share/icons/hicolor/256x256/apps/Becap.png
	cp assets/128x128/scissor.png $(HOME)/.local/share/icons/hicolor/128x128/apps/Becap.png
	cp assets/64x64/scissor.png $(HOME)/.local/share/icons/hicolor/64x64/apps/Becap.png
	cp assets/32x32/scissor.png $(HOME)/.local/share/icons/hicolor/32x32/apps/Becap.png
	cp assets/16x16/scissor.png $(HOME)/.local/share/icons/hicolor/16x16/apps/Becap.png
	cp Becap.desktop $(HOME)/.local/share/applications/Becap.desktop
	cp dist/Becap $(HOME)/.local/bin/Becap

	echo "Setting permissions"
	chmod +x $(HOME)/.local/bin/Becap
	chmod +x $(HOME)/.local/share/applications/Becap.desktop

	echo "Updating desktop database"
	update-desktop-database $(HOME)/.local/share/applications

install_linux: clean_linux gen_script_linux build_app_linux

uninstall_linux:
	echo "Removing files"
	rm -f $(HOME)/.local/bin/Becap
	rm -f $(HOME)/.local/share/icons/hicolor/256x256/apps/Becap.png
	rm -f $(HOME)/.local/share/icons/hicolor/128x128/apps/Becap.png
	rm -f $(HOME)/.local/share/icons/hicolor/64x64/apps/Becap.png
	rm -f $(HOME)/.local/share/icons/hicolor/32x32/apps/Becap.png
	rm -f $(HOME)/.local/share/icons/hicolor/16x16/apps/Becap.png
	rm -f $(HOME)/.local/share/applications/Becap.desktop

	echo "Updating desktop database"
	update-desktop-database $(HOME)/.local/share/applications
