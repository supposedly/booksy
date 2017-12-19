import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { CheckoutSessionComponent } from './checkout-session.component';

describe('CheckoutSessionComponent', () => {
  let component: CheckoutSessionComponent;
  let fixture: ComponentFixture<CheckoutSessionComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ CheckoutSessionComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(CheckoutSessionComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
