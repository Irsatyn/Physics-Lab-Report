def synthetic_pages(root, count=10):
    """Synthetic checker records only; never evidence of an actual report review."""
    from PIL import Image
    pages = []
    for i in range(count):
        p = root / ('synthetic-page-' + str(i) + '.png')
        Image.new('RGB', (32, 32), (i, 0, 0)).save(p)
        pages.append(str(p))
    return pages
