# Deploy Automatizado

## Pré-requisitos

1. Docker e Docker Compose instalados
2. Chave SSH para acesso aos servidores em `~/.ssh/`
3. Configuração do SSH em `~/.ssh/config`:

```
Host gpuserver
  HostName gpuserver.di.uminho.pt
  User g2p4
  Port <PORTA_SSH>
  IdentityFile ~/.ssh/<nome_da_chave>

Host gpuserver2
  HostName gpuserver2.di.uminho.pt
  User g2p4
  Port <PORTA_SSH>
  IdentityFile ~/.ssh/<nome_da_chave>
```

4. Chave SSH autorizada no GitHub (para o clone do repositório via agent forwarding)

## Como usar

```bash
cd deploy
docker compose run --rm ansible

# Dentro do container:
ansible all -i inventory.ini -m ping      # Testa conexão
ansible-playbook -i inventory.ini deploy.yml --limit gpuserver
```

## Variáveis configuráveis

Edita `ansible/group_vars/all.yml` para ajustar portas, nomes de modelos, etc.
