import { Component } from '@angular/core';
import { FormGroup, FormControl, FormBuilder } from '@angular/forms';

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.css']
})
export class LoginComponent {

  constructor(
  private builder: FormBuilder,
  private authService: AuthService,
  private router: Router
  ) { }

  ngOnInit() {
  }

}
