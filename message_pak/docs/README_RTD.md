# Read the Docs Setup Guide

## Quick Setup

1. **Create a Read the Docs account** at [readthedocs.org](https://readthedocs.org)
2. **Import your repository**:
   - Go to [Import a Project](https://readthedocs.org/dashboard/import/)
   - Connect your GitHub/GitLab account
   - Select the `NEST-Pakistan` repository
3. **Configure the project**:
   - **Name**: `nest-pakistan` (or your preferred name)
   - **Repository URL**: Your GitHub repository URL
   - **Default Branch**: Usually `main` or `master`
   - **Python configuration file**: `.readthedocs.yml` (already created)
   - **Documentation type**: Sphinx
4. **Build the documentation**:
   - Click "Build version" to trigger the first build
   - Read the Docs will automatically build on every push to your repository

## Your Documentation Link

Once set up, your documentation will be available at:

**https://nest-pakistan.readthedocs.io/**

(Replace `nest-pakistan` with the project name you chose during import)

## Custom Domain (Optional)

You can also set up a custom domain:
- Go to Admin → Domains
- Add your custom domain (e.g., `docs.yourdomain.com`)

## Configuration File

The `.readthedocs.yml` file in the repository root configures:
- Python version (3.11)
- Sphinx configuration location (`docs/conf.py`)
- Documentation dependencies (`docs/requirements-docs.txt`)

## Troubleshooting

### Build Fails
- Check the build logs in the Read the Docs dashboard
- Ensure all dependencies are listed in `docs/requirements-docs.txt`
- Verify `docs/conf.py` is correctly configured

### Missing Dependencies
- Add any missing packages to `docs/requirements-docs.txt`
- Rebuild the documentation

### Images Not Showing
- Ensure images are in `docs/include/` directory
- Use relative paths: `![Alt](include/image.png)`

## Automatic Builds

Read the Docs automatically builds documentation when you:
- Push to the default branch
- Create a new tag/release
- Manually trigger a build from the dashboard

## Version Management

- **Latest**: Points to the default branch (usually `main` or `master`)
- **Stable**: Points to the latest tag/release
- **Versions**: Each branch and tag can have its own documentation version


