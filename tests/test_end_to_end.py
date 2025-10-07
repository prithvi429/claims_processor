from src.main import main

def test_e2e_runs():
    # Run the main entry point to ensure no immediate errors (smoke test)
    main()
    assert True
