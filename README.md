# HealthyWays

HealthyWays is currently a Python application that lets you find the best public transport route in a given timeframe in order to avoid crowds. It was initiated during the VersusVirus Hackaton in April 2020.

A Team Project of: Agnese Sacchi, Yan Walesch, Frederik Semmel, Jona Bühler and Marino Müller

## Installation

Use the package manager [poetry](https://python-poetry.org/) to set up the evironment for HeahthyWays. Install it as described in the documentation.

Install dependencies with poetry
```bash
poetry install
```

If on Mac you have to use python 3.7 because of tensorflow 2.2.0rc2. Install  [pyenv](https://github.com/pyenv/pyenv) and run the following commands inside the virtual environment

### Initialize pyenv on fish (for bash read the pyenv readme)
Use Homebrew to install pyenv
```
brew install pyenv
```
Set the paths
```
set -Ux PYENV_ROOT $HOME/.pyenv
set -U fish_user_paths $PYENV_ROOT/bin $fish_user_paths
```
Add the following to the fish config at .config/fish/config.fish
```
# pyenv init
if command -v pyenv 1>/dev/null 2>&1
    pyenv init - | source
end
```
Now restart all the shells and then this should set the python version for a specific directory and all subdirectories
```
pyenv install 3.7.*
pyenv local 3.7.*  # Activate Python 3.7.* for the current project
```
If poetry still shows you the wrong python version, try reinstalling it.


### Google API Key
You also need your own Google API key in order to run the application. You can get it on the Google Cloud Platform

For bash
```bash
export GOOGLE_API_KEY='your api key'
```

For fish
```fish
set -Ux GOOGLE_API_KEY 'your api key'
```
### SlackBot API Keys
For the SlackBot to work you would need the Slack API Keys.

For bash
```bash
export slack_signing_secret ='SLACK_SIGNING_SECRET'
export slack_bot_token = 'SLACK_BOT_TOKEN'

```

For fish
```fish
set -Ux slack_signing_secret 'SLACK_SIGNING_SECRET'
set -Ux slack_bot_token 'SLACK_BOT_TOKEN'
```
## Usage

### Activate pyenv

You should activate the virtual environment like so
```
poetry shell
```
See poetry documentation for other usefule commands like ```poetry run``` or ```poetry build```

### Building dataset and training models

The model is stored in version control, so you should be able to run the app without training the model yourself. If you want to do so:

```
python healthyways/vbz_predictions/download_data.py
python healthyways/vbz_predictions/clean_data.py
python healthyways/vbz_predictions/build_features.py
python healthyways/vbz_predictions/train_models.py
```

### Running the app

All you need to do is run the main healthyways package

```
python healthyways
```

For the SlackBot (note that you first have to configure the Bot as well as set an https tunnel. More infos: [Slack API](https://api.slack.com/)

```
python healthyways/slackbot.py
```


## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[MIT](https://choosealicense.com/licenses/mit/)
