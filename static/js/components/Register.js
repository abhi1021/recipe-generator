const Register = () => {
    return (
        <div className="row justify-content-center">
            <div className="col-md-6">
                <div className="card">
                    <div className="card-header">
                        <h2>Register</h2>
                    </div>
                    <div className="card-body">
                        <form method="POST" action="/register">
                            <div className="mb-3">
                                <label htmlFor="name" className="form-label">Name</label>
                                <input type="text" className="form-control" id="name" name="name" required />
                            </div>
                            <div className="mb-3">
                                <label htmlFor="email" className="form-label">Email address</label>
                                <input type="email" className="form-control" id="email" name="email" required />
                            </div>
                            <div className="mb-3">
                                <label htmlFor="password" className="form-label">Password</label>
                                <input type="password" className="form-control" id="password" name="password" required minLength="8" />
                            </div>
                            <div className="mb-3">
                                <label htmlFor="confirm_password" className="form-label">Confirm Password</label>
                                <input type="password" className="form-control" id="confirm_password" name="confirm_password" required />
                            </div>
                            <div className="mb-3 form-check">
                                <input type="checkbox" className="form-check-input" id="agree_terms" name="agree_terms" required />
                                <label className="form-check-label" htmlFor="agree_terms">I agree to the <a href="#">Terms of Service</a></label>
                            </div>
                            <button type="submit" className="btn btn-primary">Register</button>
                        </form>
                    </div>
                    <div className="card-footer text-center">
                        <p>Already have an account? <a href="/login">Login here</a></p>
                    </div>
                </div>
            </div>
        </div>
    );
};
