# Secrets Vault

[![Actions Status](https://github.com/dwd/secrets-vault/workflows/Lint/badge.svg)](https://github.com/dwd/secrets-vault/actions)
[![Actions Status](https://github.com/dwd/secrets-vault/workflows/Integration%20Test/badge.svg)](https://github.com/dwd/secrets-vault/actions)

Put your secrets in git. Why not, right?

## Usage

The point of secrets-vault is to keep your secrets managed like code.

It does this by storing secrets in Ansible Vault files.

If it only did this, though, a code reviewer wouldn't have a clue what's going on. So it also adds a
plaintext schema file, which describes what secrets are in each vault file. Then it has a "lint" mode
to match up the schema files with the vault contents - so a code reviewer can just glance over the
action result and know that any secrets are in place and ready.

Each "environment" listed in the main config file will be checked in lint mode. In the normal,
export mode, it just exports a single environment.

To avoid duplication, each environment can have a "parent", from which it gains a common
set of secrets.

Secrets can be added to this base, or overridden - but a schema can define a secret as "final" (so
an attempt to override it will fail), or optional if it doesn't need a value.

Finally, secrets can be not actually secret at all.  In that case, you can set the `mask` to `False`,
and even provide a `value`.

### The Files

The files all live in ".github/secrets-vault" by default.

First, you'll need `main_config.yml`, which contains a single key `environments`, a list of environment
names. You only need to list the leaf environments she actually use directly; ones just used as parents you
can leave out.

Each environment - whether that's a leaf or not - needs two files. First, a schema file, a YAML file called
after the environment, like `prod.yml` for prod.

Here's an example:

```yaml
parent: main
secrets:
  foo:
    description: You can put some helpful stuff here.
    optional: False
    final: True
```

Then you'll need a vault file. That's a simple key-value YAML file, encrypted as an ansible vault.

### Example workflow

```yaml
name: My Workflow
on: [push, pull_request]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@master
    - name: Run action

      uses: dwd/secrets-vault@master
      id: secrets
      with:
        vault_key: ${secrets.vault_key}
        environment: prod-eu
```

### Inputs

| Input                      | Description                                                                                         |
|----------------------------|-----------------------------------------------------------------------------------------------------|
| `vault_key`                | The key for all your ansible vaults. Do me a favour, keep this in a Github Secret.                  |
| `environment` _(optional)_ | The environment you want to export, assuming export mode. If you don't supply one, it'll use `main` |
| `mode` _(optional)_        | The mode to run in. Either `export` (the default) or `lint`                                          |


### Outputs

Outputs are your secrets.

## Examples

### Using outputs

```yaml
- name: Check outputs
  run: |
    echo "Outputs - ${{ steps.secrets.outputs.foo }}"
```
