# portwait

A small, dependency-free command-line tool that waits for a TCP port to accept connections. Useful in shell scripts and local development startup sequences.

## Install

```sh
python -m pip install .
```

Requires Python 3.10 or newer. No runtime dependencies.

## Usage

```sh
portwait 127.0.0.1 5432
portwait database 5432 --timeout 60 --interval 1
python -m portwait localhost 8080 --timeout 10
```

The command makes an initial connection attempt immediately, then retries until it connects or the timeout expires. It prints a ready message and exits with status `0` on success, or prints a timeout message and exits with status `1`. Invalid arguments exit with status `2`.

Options:

- `--timeout SECONDS`: maximum wait duration (default: `30`); zero still makes one attempt
- `--interval SECONDS`: delay between failed attempts (default: `0.5`)

The probe opens and immediately closes a TCP connection. It does not send application data or check whether an HTTP endpoint is healthy. DNS resolution is handled by the operating system and can exceed the requested timeout.

## Development

```sh
python -m unittest discover -s tests -v
```

## License

MIT. See [LICENSE](LICENSE).
