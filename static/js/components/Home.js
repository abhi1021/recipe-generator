const Home = ({ hasApiKey }) => {
    return (
        <div className="container">
            {!hasApiKey && (
                <div className="alert alert-danger" role="alert">
                    <strong>Warning:</strong> Missing <code>GOOGLE_API_KEY</code>. Recipe generation will not work.
                    Please set it in your <code>.env</code> file.
                </div>
            )}

            <div className="card">
                <div className="card-header">
                    <h1 className="card-title">Generate a New Recipe</h1>
                </div>
                <div className="card-body">
                    <form action="/generate" method="POST">
                        <div className="mb-3">
                            <label htmlFor="recipe_prompt" className="form-label">What kind of recipe are you looking for?</label>
                            <input type="text" className="form-control" id="recipe_prompt" name="recipe_prompt" placeholder="e.g., 'a light summer salad' or 'a hearty beef stew'" required />
                        </div>

                        <div className="mb-3">
                            <label htmlFor="available_ingredients" className="form-label">What ingredients do you have on hand?</label>
                            <textarea className="form-control" id="available_ingredients" name="available_ingredients" rows="3" placeholder="e.g., chicken breast, tomatoes, onions, garlic"></textarea>
                        </div>

                        <div className="row g-3">
                            <div className="col-md-4">
                                <label htmlFor="servings" className="form-label">Servings</label>
                                <input type="text" className="form-control" id="servings" name="servings" placeholder="e.g., '2 people'" />
                            </div>
                            <div className="col-md-4">
                                <label htmlFor="cuisine" className="form-label">Cuisine Type</label>
                                <input type="text" className="form-control" id="cuisine" name="cuisine" placeholder="e.g., 'Italian', 'Mexican'" />
                            </div>
                            <div className="col-md-4">
                                <label htmlFor="time_pref" className="form-label">Time Preference</label>
                                <input type="text" className="form-control" id="time_pref" name="time_pref" placeholder="e.g., 'under 30 minutes'" />
                            </div>
                        </div>

                        <div className="d-grid gap-2 mt-4">
                            <button type="submit" className="btn btn-primary btn-lg">Generate Recipe</button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    );
};
