import org.apache.commons.io.FileUtils;
import org.jsoup.Jsoup;
import org.jsoup.nodes.Document;
import org.jsoup.nodes.Element;
import org.jsoup.select.Elements;
import java.io.File;
import java.io.IOException;
import java.net.URL;
import java.util.concurrent.*;

public class PdfScraper {

	private static final String BASE_URL = "https://papers.nips.cc";
	private static final int START_YEAR = 2017; 
	private static final int END_YEAR = 2023;   
	private static final int MAIN_THREAD_POOL_SIZE = 10;  // Thread pool size for years
	private static final int YEAR_THREAD_POOL_SIZE = 20;  // Thread pool size for papers per year

	public static void main(String[] args) {
		ExecutorService mainExecutor = Executors.newFixedThreadPool(MAIN_THREAD_POOL_SIZE);

		try {
			File mainDownloadDir = new File("downloads");
			if (!mainDownloadDir.exists()) {
				mainDownloadDir.mkdir();
				System.out.println("Created directory: downloads");
			}

			for (int year = START_YEAR; year <= END_YEAR; year++) {
				int finalYear = year;
				mainExecutor.submit(() -> {
					File yearDownloadDir = new File(mainDownloadDir, String.valueOf(finalYear));
					if (!yearDownloadDir.exists()) {
						yearDownloadDir.mkdir();
						System.out.println("Created directory for year " + finalYear);
					}

					ExecutorService yearExecutor = Executors.newFixedThreadPool(YEAR_THREAD_POOL_SIZE);

					String yearPath = "/paper_files/paper/" + finalYear;
					String yearUrl = BASE_URL + yearPath;

					System.out.println("Fetching year URL: " + yearUrl);

					try {
						Document yearPage = Jsoup.connect(yearUrl).get();
						// Select all paper links (HTML links to papers in that year)
						Elements paperLinks = yearPage.select("a[href]");

						if (paperLinks.isEmpty()) {
							System.out.println("No paper links found for year " + finalYear);
						}
						for (Element paperLink : paperLinks) {
							String paperPath = paperLink.attr("href");

							if (finalYear <= 2020 && paperPath.contains("Abstract.html")) {
								yearExecutor.submit(() -> downloadPaperForOlderYears(paperPath, yearDownloadDir));
							} else if (finalYear > 2020) {
								yearExecutor.submit(() -> downloadPaper(paperPath, yearDownloadDir));
							}
						}

					} catch (IOException e) {
						System.out.println("Error fetching year page for year " + finalYear + ": " + e.getMessage());
					} finally {
						yearExecutor.shutdown();
						try {
							yearExecutor.awaitTermination(Long.MAX_VALUE, TimeUnit.MILLISECONDS);
						} catch (InterruptedException e) {
							System.out.println("Year Executor Interrupted: " + e.getMessage());
						}
					}
				});
			}

			mainExecutor.shutdown();
			mainExecutor.awaitTermination(Long.MAX_VALUE, TimeUnit.MILLISECONDS);
			System.out.println("All PDFs downloaded.");
		} catch (InterruptedException e) {
			System.out.println("An error occurred: " + e.getMessage());
		}
	}

	private static void downloadPaperForOlderYears(String paperPath, File downloadDir) {
		try {
			String paperUrl = BASE_URL + paperPath;
			Document paperPage = Jsoup.connect(paperUrl).get();
			Element pdfLinkElement = paperPage.selectFirst("a[href$=.pdf]");

			if (pdfLinkElement != null) {
				String pdfPath = pdfLinkElement.attr("href");
				String pdfUrl = BASE_URL + pdfPath;

				// Extract the proper file name for the PDF
				String fileName = extractFileName(paperPage, pdfPath);
				System.out.println("Downloading: " + fileName);

				// Download the PDF and save it in the year folder
				File destinationFile = new File(downloadDir, fileName);
				FileUtils.copyURLToFile(new URL(pdfUrl), destinationFile);

				System.out.println("Successfully downloaded: " + fileName);
			} else {
				System.out.println("No PDF link found for paper: " + paperUrl);
			}

		} catch (IOException e) {
			System.out.println("Error downloading paper: " + e.getMessage());
		}
	}

	private static void downloadPaper(String paperPath, File downloadDir) {
		try {
			String paperUrl = BASE_URL + paperPath;
			Document paperPage = Jsoup.connect(paperUrl).get();
			Element pdfLinkElement = paperPage.selectFirst("a[href$=.pdf]");

			if (pdfLinkElement != null) {
				String pdfPath = pdfLinkElement.attr("href");
				String pdfUrl = BASE_URL + pdfPath;

				// Extract the proper file name for the PDF
				String fileName = extractFileName(paperPage, pdfPath);
				System.out.println("Downloading: " + fileName);

				// Download the PDF and save it in the year folder
				File destinationFile = new File(downloadDir, fileName);
				FileUtils.copyURLToFile(new URL(pdfUrl), destinationFile);

				System.out.println("Successfully downloaded: " + fileName);
			} else {
				System.out.println("No PDF link found for paper: " + paperUrl);
			}
		} catch (IOException e) {
			System.out.println("Error downloading paper: " + e.getMessage());
		}
	}

	private static String extractFileName(Document paperPage, String pdfPath) {
		String paperTitle = paperPage.title(); 
		if (paperTitle == null || paperTitle.isEmpty()) {
			paperTitle = pdfPath.substring(pdfPath.lastIndexOf("/") + 1, pdfPath.lastIndexOf("."));
		}
		paperTitle = paperTitle.replaceAll("[^a-zA-Z0-9_\\-]", "_");
		return paperTitle + ".pdf";
	}
}