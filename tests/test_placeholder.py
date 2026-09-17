from mi_primer_proyecto_ia import main


def test_main_runs(capsys):
    main()
    captured = capsys.readouterr()
    assert "mi-primer-proyecto-ia" in captured.out
