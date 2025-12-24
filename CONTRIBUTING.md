# Contribution guidelines

Contributing to this project should be as easy and transparent as possible, whether it's:

- Reporting a bug
- Discussing the current state of the code
- Submitting a fix
- Proposing new features

## Github is used for everything

Github is used to host code, to track issues and feature requests, as well as accept pull requests.

Pull requests are the best way to propose changes to the codebase.

1. Fork the repo and create your branch from `main`.
2. If you've changed something, update the documentation.
3. Make sure your code lints (using `scripts/lint`).
4. Make sure tests pass and you have added coverage as appropriate (using `scripts/test`).
5. Issue that pull request!

## Any contributions you make will be under the MIT Software License

In short, when you submit code changes, your submissions are understood to be under the same [MIT License](http://choosealicense.com/licenses/mit/) that covers the project. Feel free to contact the maintainers if that's a concern.

## Report bugs using Github's [issues](../../issues)

GitHub issues are used to track public bugs.
Report a bug by [opening a new issue](../../issues/new/choose); it's that easy!

## Write bug reports with detail, background, and sample code

**Great Bug Reports** tend to have:

- A quick summary and/or background
- Steps to reproduce
  - Be specific!
  - Give sample code if you can.
- What you expected would happen
- What actually happens
- Notes (possibly including why you think this might be happening, or stuff you tried that didn't work)

People *love* thorough bug reports. I'm not even kidding.

## Use a Consistent Coding Style

Use [black](https://github.com/ambv/black) to make sure the code follows the style.

## Test your code modification

This custom component is based on [integration_blueprint template](https://github.com/ludeeus/integration_blueprint).

It comes with development environment in a container, easy to launch
if you use Visual Studio Code. With this container you will have a stand alone
Home Assistant instance running and already configured with the included
[`configuration.yaml`](./config/configuration.yaml)
file.

## Creating a Release

This project uses a streamlined, manifest-first release process:

### Release Process

1. **Update the version** in [custom_components/inception/manifest.json](custom_components/inception/manifest.json)
   ```bash
   # Example: Change version from "4.0.0-beta1" to "4.1.0"
   vim custom_components/inception/manifest.json
   ```

2. **Commit and push** the version change to the `main` branch
   ```bash
   git add custom_components/inception/manifest.json
   git commit -m "Bump version to 4.1.0"
   git push origin main
   ```

3. **Trigger the release workflow** via GitHub Actions
   - Go to: [Actions → Release → Run workflow](../../actions/workflows/release.yml)
   - Click "Run workflow" button
   - Or use the GitHub CLI: `gh workflow run release.yml`

The workflow will automatically:
- Read the version from `manifest.json`
- Detect if it's a prerelease (based on `-beta`, `-alpha`, or `-rc` suffix)
- Create a git tag (e.g., `4.1.0`)
- Generate release notes from recent commits
- Build and upload the integration ZIP file
- Publish the GitHub release

### Version Format

Versions must follow semantic versioning with optional prerelease suffix:
- Stable releases: `X.Y.Z` (e.g., `4.1.0`)
- Prereleases: `X.Y.Z-suffix` (e.g., `4.1.0-beta1`, `4.1.0-alpha2`, `4.1.0-rc1`)

Prereleases are automatically detected and marked appropriately in GitHub releases.

### Workflow Options

The release workflow supports optional inputs:
- **Draft release**: Create as draft for manual review before publishing
- **Custom notes**: Add custom release notes (prepended to auto-generated notes)

### Troubleshooting

**Tag already exists**: If the workflow fails because the tag already exists, either:
- Update the version in `manifest.json` to a new version, or
- Delete the existing tag: `git tag -d X.Y.Z && git push origin :refs/tags/X.Y.Z`

**Invalid version format**: Ensure the version in `manifest.json` matches the required format (e.g., `4.1.0` or `4.1.0-beta1`)

## License

By contributing, you agree that your contributions will be licensed under its MIT License.
