> Tools for running the Super Mario Galaxy Movie web app locally

- How to use

  1. Enable webview debug for Nintendo Today! app. (Find a way to do it yourself)
  2. Enable adb debug and connect to a PC
  3. Open Nintendo Today! app goto the smgm event page
  4. Go to chrome://inspect#devices on your PC
  5. Click on "inspect" under Nintendo Today's WebView.
  6. In DevTools, Network page, Press Ctrl+R to refresh and wait for all resources to load.
  7. Click "Download" icon to download all resources as HAR file.
  8. Find Cookie and Authorization in Headers tab (Note that cookie only used for GET method and Authorization for fetch method)
  9. Rename har.token.example to har.token, then paste the tokens found in the previous step
  10. Run ```./har.py path/of/har/file``` download all resources to the current directory
  11. Edit mii.config to configure nick name, birthday, language
  12. Run ```./inject```
  13. Run a web server in the current directory, for example ```python3 -m http.server```
 

- How to configure

  1. Run ```./update.py``` to refresh configure
  2. Run ```./drawn_card.py``` can randomly add card-drawing animations to the cards page
  3. Run ```./drwan_card.py -r``` to remove card drawing
  4. Edit ``mii_images/me.png`` replace Mii avatar
