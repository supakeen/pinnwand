# Contributing to Pinnwand
Welcome to the Pinnwand contributing guide! Your interest in improving Pinnwand is greatly appreciated. In this document, you'll find the steps and guidelines that will help you contribute effectively to the project. We aim to maintain a welcoming and collaborative environment, and every contribution counts, no matter how big or small.


## Getting the code
In order to be able to contribute, you'll need to have the repository cloned on your local machine.

To do that, you'll need to:
* [Make a fork](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/fork-a-repo) of the [pinnwand repo](https://github.com/supakeen/pinnwand).
  * This will have a copy of `pinnwand` as your remote repository on `Github`

* [Clone your forked repository](https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository)
  * This will allow you to pull/push changes to your remote `pinnwand` fork.

## Setting up the environment
This can be done in multiple ways. However, `pinnwand` used [PDM](https://pdm-project.org/latest/) to manage dependencies so we'll explain how to setup your environment with it.

* [Install DPM](https://pdm-project.org/latest/#installation)
  * This is needed in order to add/update/lock dependencies


* Installing the dependencies
This is as simple as running the following command from the project's root directory
    ```bash
        pdm install
    ```

    This will create the virtual environment for you automatically.
    If you want more control on the creation/reuse of virtual environments, please consult the [official docs](https://pdm-project.org/latest/usage/venv/).

## Code style
We use [black](https://black.readthedocs.io/en/stable) as our code formatter, so the code style is dictated/enforced by it.

To check if there are needed changes to styling, you can run this command
```bash
python -m black src/pinnwand
```

## Running tests
To ensure that contributions do not alter expected behavior or break things, the project has 2 main test suites, [e2e](test/e2e) and [integration](test/integration).

The [e2e](test/e2e) runs tests on a browser, to ensure that the user interface displays correct content and behaves correctly from a GUI perspective.
The [integration](test/integration) runs various integration/unit tests to make sure that different parts of the app behave correctly both independently and with others

* e2e tests are ran using the following command

    ```bash
    pytest --e2e test/e2e --html=test/e2e/report/index.html --self-contained-html
    ```

* integration tests are ran using the following command:

    ```bash
    pytest --cov=pinnwand test/integration
    ```

## Running the necessary checks automatically
It's good practice to run code style checks, tests, static code analysis, etc. all together.
Having to execute these commands each time manually can become tedious, which is why we use the `pre-commit` package to setup 
a client-side [git hook](https://git-scm.com/book/en/v2/Customizing-Git-Git-Hooks) and run all of these checks automatically.

Setting up the hook is really simple, all you need to do is:
```bash
pre-commit install
```

> Note: Make sure you have the optional dev dependencies installed in order to be able to use pre-commit.

## Working on features/bug fixes

Once everything is set up, you can start developing a feature/fixing a bug locally.
Changes are merged thanks to `Pull Requests`.

If `Pull Requests` are an unfamiliar concept, you can read more about [what they are](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/about-pull-requests), and about 
[creating them](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request).

All `Pull Request`s will need to be reviewed and approved before they can merged into the master branch.

> Note: All new features should be accompanied with a test that covers them.

### Adding New Dependencies

We strive to keep Pinnwand lightweight and simple, therefore, before adding a new dependency, please consider the following:
- Can the functionality be achieved without an additional dependency?
- Is the dependency actively maintained and well-regarded in the community?

If a new dependency is justified, discuss it in your pull request or open an issue for discussion. To add it:
```bash
pdm add your-dependency
pdm export -o requirements.txt -f requirements
```