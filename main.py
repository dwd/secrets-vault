import gh


def main():
    with gh.GithubAction() as gha:
        my_input = gha.input('MY_INPUT')
        my_output = f'Hello {my_input}'
        gha.set_output('myOutput', my_output)


if __name__ == "__main__":
    main()
