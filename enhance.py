import json

import typer
import jq
import subprocess
import sys
app = typer.Typer()

@app.callback(invoke_without_command=True)
def main(
    value: str = typer.Option(...,"--file", "-f", allow_dash=True, help="File containing jsonln or - for stdin"),
    input: str = typer.Option(..., "--input", "-i", help="jq filter to select input you want to pass to the provided command"),
    output: str = typer.Option(..., "--output", "-o", help="key you would like to inject the command output into"),
    command: str = typer.Option(..., "--command", "-c", help="command you want to execute can contain pipes"),
    replstr: str = typer.Option("{}", "--replstr", "-I", help="Replace string with input data in the command (think xargs -I)"),
    json_command: bool = typer.Option(False, "--jsoncommand", "-j", help="If the command outputs json set this flag"),
    pipe: bool = typer.Option(False, "--pipe", "-p", help="If the input needs to be piped into your command use this flag"),
    array: bool = typer.Option(False, "--array", "-a", help="should the output be split on newlines or as a raw string?"),
):
    if value == "-":
        file = sys.stdin
    else:
        file = open(value, encoding='utf-8')
    for index, line in enumerate(file):
        parsed = json.loads(line)
        input_value = jq.compile(input).input(parsed).first()
        # if array:
        #     typer.echo(f"Good day Ms. {input}.")
        # else:
        if pipe:
            output_value = subprocess.run(command, shell=True, capture_output=True, input=input_value,
                    text=True)
        else:
            final_command = command.replace(replstr, input_value)
            output_value = subprocess.run(final_command, shell=True,text=True, capture_output=True)
        if json_command:
            results = json.loads(output_value.stdout)
        else:
            if array:
                results = output_value.stdout.rstrip("\n").split("\n")
            else:
                results = output_value.stdout
        parsed[output] = results
        typer.echo(json.dumps(parsed))
    file.close()


if __name__ == "__main__":
    app()