[s.cympfh.cc](http://s.cympfh.cc)

個人サーバー `s.cympfh.cc` への Ansible デプロイ。詳細は [AGENTS.md](AGENTS.md)。

## 必要なもの

- [uv](https://docs.astral.sh/uv/)
- Ansible: **ansible >= 11.7.0**（ansible-core 2.18 系）。`uv sync` で入ります
  - `ansible.cfg` は `inventory` キーを使用。旧来の `hostfile` が無視・削除された現行バージョンが前提です
- vault 付き playbook（`video.yml`, `eliza.yml` など）の実行には vault パスワードが必要です

## デプロイ

```bash
uv sync
uv run ansible-playbook playbooks/<name>.yml
```

vault が必要な playbook はパスワードファイルを指定します:

```bash
ANSIBLE_VAULT_PASSWORD_FILE=~/.ansible-vault-pass uv run ansible-playbook playbooks/video.yml
```
