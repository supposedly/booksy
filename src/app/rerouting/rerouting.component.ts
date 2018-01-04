import { Component, OnInit } from '@angular/core';
import { Router, ActivatedRoute } from '@angular/router';

@Component({
  selector: 'app-rerouting',
  templateUrl: './rerouting.component.html',
  styleUrls: ['./rerouting.component.css']
})
export class ReroutingComponent implements OnInit {
  redirect: string = '/';
  
  constructor(
    private router: Router,
    private route: ActivatedRoute
  ) {}

  ngOnInit() {
    this.redirect = this.route.snapshot.queryParams['redirect'] || '/';
    this.router.navigateByUrl(this.redirect, {});
  }

}
