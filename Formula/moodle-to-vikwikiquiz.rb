# frozen_string_literal: true

class MoodleToVikwikiquiz < Formula
  include Language::Python::Virtualenv

  desc "A CLI for converting a graded Moodle quiz HTML to a vik.wiki quiz wikitext."
  homepage "https://github.com/gy-mate/homebrew-moodle-to-vikwikiquiz"
  url "https://github.com/gy-mate/homebrew-moodle-to-vikwikiquiz/archive/1.0.13.tar.gz"
  license "GPl-3.0"
  sha256 ""
  head "https://github.com/gy-mate/homebrew-moodle-to-vikwikiquiz.git"

  depends_on "python@3.12"

  def install
    virtualenv_install_with_resources
  end

  test do
    system "#{bin}/moodle-to-vikwikiquiz", "--version"
  end
end
