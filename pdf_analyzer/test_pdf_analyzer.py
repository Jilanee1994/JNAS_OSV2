from pytest import fixture, raises
from pdf_analyzer.pdf_analyzer import PdfAnalyzer

@fixture
def sample_pdf(tmp_path):
    content = "Name: John Doe\nAge: 30\nOccupation: Engineer\n"
    pdf_path = tmp_path / "sample.pdf"
    with pdf_path.open("w") as f:
        f.write(content)
    return pdf_path

def test_extract_text_happy_path(sample_pdf):
    analyzer = PdfAnalyzer(str(sample_pdf))
    result = analyzer.extract_text()
    assert result == {'Name': ['John Doe'], 'Age': ['30'], 'Occupation': ['Engineer']}

def test_extract_text_empty_file(tmp_path):
    empty_pdf = tmp_path / "empty.pdf"
    with empty_pdf.open("w") as f:
        pass
    analyzer = PdfAnalyzer(str(empty_pdf))
    with raises(FileNotFoundError):
        analyzer.extract_text()

def test_get_page_count(sample_pdf):
    analyzer = PdfAnalyzer(str(sample_pdf))
    assert analyzer.get_page_count() == 1

def test_analyze_pages_happy_path(sample_pdf):
    analyzer = PdfAnalyzer(str(sample_pdf))
    result = analyzer.analyze_pages()
    expected_result = [
        {"page": "1", "content": "Name: John Doe\nAge: 30\nOccupation: Engineer"}
    ]
    assert result == expected_result

def test_analyze_pages_empty_file(tmp_path):
    empty_pdf = tmp_path / "empty.pdf"
    with empty_pdf.open("w") as f:
        pass
    analyzer = PdfAnalyzer(str(empty_pdf))
    with raises(FileNotFoundError):
        analyzer.analyze_pages()