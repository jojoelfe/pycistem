#include "../core/gui_core_headers.h"

AbInitioPlotPanel::AbInitioPlotPanel(wxWindow* parent, wxWindowID id, const wxPoint& pos, const wxSize& size, long style)
: AbInitioPlotPanelParent(parent, id, pos, size, style)
{
//	LikelihoodSizer = new wxBoxSizer( wxVERTICAL );
	SigmaSizer = new wxBoxSizer( wxVERTICAL );

	//LikelihoodPanel->SetSizer (LikelihoodSizer);
	SigmaPanel->SetSizer (SigmaSizer);

	//LikelihoodPanel->Layout();
	SigmaPanel->Layout();

//	LikelihoodSizer->Fit(LikelihoodPanel);
	SigmaSizer->Fit(SigmaPanel);

//	likelihood_vector_layer = new mpFXYVector(("-LogP"));
	sigma_vector_layer = new mpFXYVector(("Sigma"));

//	likelihood_vector_layer->ShowName(false);
	sigma_vector_layer->ShowName(false);

	wxPen vectorpen(*wxBLUE, 2, wxSOLID);

//	likelihood_vector_layer->SetContinuity(true);
//	likelihood_vector_layer->SetPen(vectorpen);
//	likelihood_vector_layer->SetDrawOutsideMargins(false);

	sigma_vector_layer->SetContinuity(true);
	sigma_vector_layer->SetPen(vectorpen);
	sigma_vector_layer->SetDrawOutsideMargins(false);

	wxFont graphFont(9, wxFONTFAMILY_DEFAULT, wxFONTSTYLE_NORMAL, wxFONTWEIGHT_NORMAL);

//	likelihood_plot_window = new mpWindow( LikelihoodPanel, -1, wxPoint(0,0), wxSize(100, 100), wxSUNKEN_BORDER );
	sigma_plot_window = new mpWindow( SigmaPanel, -1, wxPoint(0,0), wxSize(100, 100), wxSUNKEN_BORDER );

//	likelihood_xaxis = new mpScaleX(wxT("Round No."), mpALIGN_BOTTOM, true, mpX_NORMAL);
	sigma_xaxis = new mpScaleX(wxT("Round No."), mpALIGN_BOTTOM, true, mpX_NORMAL);

//	likelihood_yaxis = new mpScaleY(wxT("Avg. LogP"), mpALIGN_LEFT, true);
	sigma_yaxis = new mpScaleY(wxT("Avg. σ"), mpALIGN_LEFT, true);

//	likelihood_xaxis->SetFont(graphFont);
	sigma_xaxis->SetFont(graphFont);

//	likelihood_yaxis->SetFont(graphFont);
	sigma_yaxis->SetFont(graphFont);

//	likelihood_xaxis->SetDrawOutsideMargins(false);
	sigma_xaxis->SetDrawOutsideMargins(false);

//	likelihood_yaxis->SetDrawOutsideMargins(false);
	sigma_yaxis->SetDrawOutsideMargins(false);

//	likelihood_plot_window->SetMargins(20,20,40,70);
	sigma_plot_window->SetMargins(20,20,40,70);

//	likelihood_plot_window->AddLayer(likelihood_xaxis);
//	likelihood_plot_window->AddLayer(likelihood_yaxis);
//	likelihood_plot_window->AddLayer(likelihood_vector_layer);
//	LikelihoodSizer->Add(likelihood_plot_window, 1, wxEXPAND);
//	likelihood_plot_window->EnableDoubleBuffer(true);
//	likelihood_plot_window->EnableMousePanZoom(false);

	sigma_plot_window->AddLayer(sigma_xaxis);
	sigma_plot_window->AddLayer(sigma_yaxis);
	sigma_plot_window->AddLayer(sigma_vector_layer);
	SigmaSizer->Add(sigma_plot_window, 1, wxEXPAND);
	sigma_plot_window->EnableDoubleBuffer(true);
	sigma_plot_window->EnableMousePanZoom(false);
}

void AbInitioPlotPanel::Clear()
{
	Freeze();

//	likelihood_vector_layer->Clear();
	sigma_vector_layer->Clear();

	round_data.clear();
//	likelihood_data.clear();
	sigma_data.clear();

	Thaw();
}

void AbInitioPlotPanel::Draw()
{
	Freeze();

//	likelihood_vector_layer->SetData(round_data, likelihood_data);
	sigma_vector_layer->SetData(round_data, sigma_data);

//	likelihood_plot_window->Fit();
//	likelihood_plot_window->Fit(1, round_data.size(), likelihood_plot_window->GetDesiredYmin(),  likelihood_plot_window->GetDesiredYmax());

	sigma_plot_window->Fit();
	sigma_plot_window->Fit(1, round_data.size(), sigma_plot_window->GetDesiredYmin(),  sigma_plot_window->GetDesiredYmax());

//	likelihood_plot_window->UpdateAll();
	sigma_plot_window->UpdateAll();

	Thaw();
}

void AbInitioPlotPanel::AddPoints(float round, float sigma)
{
	round_data.push_back(round);
//	likelihood_data.push_back(likelihood);
	sigma_data.push_back(sigma);
}


AbInitioPlotPanel::~AbInitioPlotPanel()
{
//	delete likelihood_plot_window;
	delete sigma_plot_window;
}
