# s.cympfh.cc

個人サーバー `s.cympfh.cc` への Ansible デプロイ。アプリ本体は各 GitHub リポジトリ。ここは build / run / nginx 経路だけ持つ。

対象ホスト: `inventory/hosts` の `deploy`（`s.cympfh.cc`, user `ubuntu`）。作業ディレクトリはリモートの `/home/ubuntu/git/<tag>/`。

## コマンド

```bash
uv sync
uv run ansible-playbook playbooks/<name>.yml
```

vault が必要な playbook（`video.yml`, `eliza.yml`, `scroll.yml`, `mini-hsk5.yml`）は `--ask-vault-pass` か `ANSIBLE_VAULT_PASSWORD_FILE`。

`ansible.cfg` の `hostfile = inventory` は現行 Ansible では `inventory` の旧名。inventory は `inventory/`。SSH は `ForwardAgent=yes`。

Python は `.python-version` の 3.12。依存は `pyproject.toml` の ansible のみ。

## ディレクトリ

```
inventory/hosts                  # ホスト
inventory/group_vars/all/vars.yml   # vault への参照（平文）
inventory/group_vars/all/vault.yml  # ansible-vault AES256。中身を平文で書かない
playbooks/<service>.yml          # サービス 1 ファイル
playbooks/nginx/                 # リバースプロキシ（ローカル copy）
roles/docker_build/              # clone or copy → docker build
roles/docker_deploy/             # stop/rm → docker run
roles/screen_deploy/             # 未使用
```

## ロール

`docker_build`:

- `copy_files` あり → ローカルファイルを `/home/ubuntu/git/<tag>/` に copy（nginx）
- `repo` あり → `git clone/update` して同じパスへ（force しない）
- その後 `docker build -f .../Dockerfile -t <tag> ...`

`docker_deploy`: 既存コンテナを stop/rm してから `docker run`。分岐は変数:

| 変数 | 用途 |
|---|---|
| `full_command` | コマンド文字列をそのまま実行。現行 playbook の大半 |
| `port_host` + `port_container` + `command` | `-p` 付きで `command` を末尾に付ける。`date.yml` のみ |
| ポートなし + `command` | バッチ用 |
| ポートだけ | コマンドなしサーバー |

コンテナ名とイメージ名はどちらも `tag`。

## サービス

nginx (`playbooks/nginx/files/nginx.conf`) が 80 で path を各ポートへ。443 は Let's Encrypt (`/etc/letsencrypt/live/s.cympfh.cc/`) で TLS 終端し、同一コンテナの :80 へプロキシ。ACME 用 webroot は `/var/www/certbot`。更新はホスト cron（certbot docker + `nginx -s reload`）。

| playbook | tag | 公開 path | ポート | ソース |
|---|---|---|---|---|
| `date.yml` | dateserver | `/date` | 8000 | cympfh/date-server |
| `journal.yml` | journal | `/journal` | 8081 | cympfh/journal.py |
| `search.yml` | cympfh-search | （nginx 側コメントアウト） | 8083 | cympfh/cympfh-search |
| `book.yml` | booklog-database | `/book` | 8084 | cympfh/booklog-database |
| `shields.yml` | shields | `/shields` | 8092 | cympfh/shields |
| `chilingo.yml` | chilingo | `/chilingo` | 8094 | cympfh/chilingo |
| `video.yml` | video | `/video` | 8095 | cympfh/video |
| `eliza.yml` | eliza | `/eliza` | 8096 | cympfh/eliza-agent-server |
| `mini-hsk5.yml` | mini-hsk5 | `/mini-hsk5/` | 8097 | cympfh/mini-hsk-5 |
| `scroll.yml` | scroll | なし（バッチ） | — | cympfh/tw-fav-scroll |
| `nginx/main.yml` | nginx | 80/443 | — | `playbooks/nginx/files/` |

nginx に経路だけあって playbook が無いもの: `/anime` :8087, `/rss` :8091。コメントアウト: `/search`, `/othello`, `/dashboard`。

特殊な volume / env:

- `journal`: `-v /home/ubuntu/git/journal/data:/app/data`
- `search`: `~/git/cympfh.github.io/` をマウント
- `eliza`: `$HOME/eliza-memory:/app/.memory` と vault 由来の env
- `mini-hsk5`: `/home/ubuntu/mini-hsk5-data:/data`（`HSK5_DATA_DIR`）。`XAI_API_KEY`（`mini_hsk5.xai_api_key` ← vault）。起動はイメージ CMD
- `video`: `YOUTUBE_API_KEY`（`youtube.api_key` ← vault）。`/home/ubuntu/firefox/cookie.txt` を同パスで `:ro` bind（yt-dlp）
- `scroll`: `~/scroll-out:/out`。`twitter.vimdot.twurl` を参照するが、`vars.yml` から twitter は削除済み。動かすなら vault 参照を戻す
- `nginx`: `/etc/letsencrypt:/etc/letsencrypt:ro` と `/var/www/certbot:/var/www/certbot:ro`

## 秘密情報

- `vault.yml` は暗号化のまま扱う。decrypt 結果をファイルに残さない。commit しない
- 秘密は `vars.yml` 経由で `{{ vault.* }}` を参照する。playbook に直書きしない
- 現行の vault 参照: `vault.youtube.api_key`, `vault.eliza.*`, `vault.mini_hsk5.xai_api_key`

## サービス追加

1. アプリ側リポジトリに Dockerfile を置く
2. `playbooks/<name>.yml` を既存に合わせて書く（`hosts: deploy`, `repo`/`tag`/`full_command`, roles `docker_build` + `docker_deploy`）
3. 公開するなら `playbooks/nginx/files/nginx.conf` に `location` を足し、`nginx/main.yml` も当てる
4. 秘密が要るなら vault に足して `vars.yml` から参照

## やってはいけないこと

- リモートの `/home/ubuntu/git/<tag>/` を手元の編集で上書きする想定で書かない。ソースは GitHub。nginx だけ `copy_files`
- `docker_build` の git は `force: no`。リモートのローカル変更は残る
- `repos/cympfh-search` は空の gitlink。search の実体はリモート clone
