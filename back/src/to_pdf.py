import markdown2
from weasyprint import HTML

def markdown_to_html(markdown_text):
    return markdown2.markdown(markdown_text)

def html_to_pdf(html_content, output_pdf):
    HTML(string=html_content).write_pdf(output_pdf)
    print(f"PDF успешно создан: {output_pdf}")

def markdown_to_pdf(markdown_text, output_pdf):
    html_content = markdown_to_html(markdown_text)
    html_to_pdf(html_content, output_pdf)

if __name__ == "__main__":
    markdown_text = """
    # Заголовок 1

    Это пример текста в формате Markdown.

    ## Заголовок 2

    - Первый элемент списка
    - Второй элемент списка

    **Жирный текст** и *курсив*.

    [Ссылка](https://example.com)
    """

    output_pdf_file = "output.pdf"
    markdown_to_pdf(markdown_text, output_pdf_file)
