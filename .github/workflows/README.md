# Pushing and Building Release on GitHub Workflow

## Steps to Push and Build a Release

1. **Checkout the main branch:**

    ```sh
    git checkout main
    ```

2. **Pull the latest changes from the main branch:** 

    ```sh
    git pull origin main
    ```

3. **Tag the release:**

    ```sh
    git tag <tag-version>
    ```

4. **Push the changes and the tag to the remote repository:**

    ```sh
    git push origin main <tag-version>
    ```

## Tagging Conventions

- `vx.x.x` tags a latest release.
- `vx.x.x.alpha` tags a pre-release.