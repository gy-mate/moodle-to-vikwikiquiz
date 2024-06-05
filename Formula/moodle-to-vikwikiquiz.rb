# frozen_string_literal: true

class MoodleToVikwikiquiz < Formula
  include Language::Python::Virtualenv

  desc "A CLI for converting a graded Moodle quiz HTML to a vik.wiki quiz wikitext."
  homepage "https://github.com/gy-mate/homebrew-moodle-to-vikwikiquiz"
  url "https://github.com/gy-mate/homebrew-moodle-to-vikwikiquiz/archive/1.0.22.tar.gz"
  license "GPl-3.0"
  sha256 ""
  head "https://github.com/gy-mate/homebrew-moodle-to-vikwikiquiz.git"

  depends_on "python@3.12"

  resource "beautifulsoup4" do
      url "https://files.pythonhosted.org/packages/b3/ca/824b1195773ce6166d388573fc106ce56d4a805bd7427b624e063596ec58/beautifulsoup4-4.12.3.tar.gz"
      sha256 "74e3d1928edc070d21748185c46e3fb33490f22f52a3addee9aee0f4f7781051"
  end

  def install
    virtualenv_install_with_resources
  end

  test do
    system "#{bin}/moodle-to-vikwikiquiz", "--version"
  end
end
